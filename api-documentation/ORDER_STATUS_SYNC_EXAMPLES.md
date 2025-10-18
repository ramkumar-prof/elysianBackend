# Order Status Synchronization Examples

## Overview

The `get_order_details` API now includes intelligent status synchronization with the payment gateway. When an order has a 'PENDING' payment status, the system automatically checks with PhonePe gateway for the latest status and updates the database accordingly.

## How It Works

### 1. Status Check Trigger
- **Condition**: Order payment status is 'PENDING'
- **Action**: Automatically calls `get_payment_status(order_id)` from payment gateway
- **Frequency**: Every time order details are requested (real-time check)

### 2. Status Mapping
```python
# Gateway status → Internal status mapping
status_mapping = {
    'COMPLETED': 'COMPLETED',  # Payment successful
    'FAILED': 'FAILED',        # Payment failed
    'PENDING': 'PENDING'       # Still processing
}
```

### 3. Cascading Updates
When payment status changes:
- **Payment Status**: Updated in both Order and Payment tables
- **Order Status**: Automatically updated based on payment status
  - `COMPLETED` payment → `CONFIRMED` order
  - `FAILED` payment → `CANCELLED` order
- **Transaction ID**: Updated from gateway response
- **Additional Info**: Stores last check timestamp and gateway response

## Example Scenarios

### Scenario 1: Payment Completed

**Initial State (in database):**
```json
{
    "order": {
        "id": 123,
        "payment_status": "PENDING",
        "order_status": "PENDING"
    },
    "payment": {
        "payment_status": "PENDING",
        "transaction_id": null
    }
}
```

**Gateway Response:**
```json
{
    "state": "COMPLETED",
    "transaction_id": "TXN789456123"
}
```

**Updated State (after API call):**
```json
{
    "order": {
        "id": 123,
        "payment_status": "COMPLETED",  // ✅ Updated
        "order_status": "CONFIRMED"     // ✅ Updated
    },
    "payment": {
        "payment_status": "COMPLETED",  // ✅ Updated
        "transaction_id": "TXN789456123", // ✅ Updated
        "additional_info": {
            "last_checked": "2024-01-01T10:05:00Z",
            "gateway_response": "..."
        }
    },
    "status_updated": true  // ✅ Indicates update occurred
}
```

### Scenario 2: Payment Failed

**Initial State:**
```json
{
    "order": {
        "payment_status": "PENDING",
        "order_status": "PENDING"
    }
}
```

**Gateway Response:**
```json
{
    "state": "FAILED"
}
```

**Updated State:**
```json
{
    "order": {
        "payment_status": "FAILED",     // ✅ Updated
        "order_status": "CANCELLED"    // ✅ Updated
    },
    "payment": {
        "payment_status": "FAILED"     // ✅ Updated
    },
    "status_updated": true
}
```

### Scenario 3: Still Pending

**Initial State:**
```json
{
    "order": {
        "payment_status": "PENDING"
    }
}
```

**Gateway Response:**
```json
{
    "state": "PENDING"
}
```

**Updated State:**
```json
{
    "order": {
        "payment_status": "PENDING"    // ✅ No change needed
    },
    "payment": {
        "additional_info": {
            "last_checked": "2024-01-01T10:05:00Z"  // ✅ Updated check time
        }
    },
    "status_updated": false  // ✅ No status change
}
```

### Scenario 4: Already Completed Order

**Initial State:**
```json
{
    "order": {
        "payment_status": "COMPLETED",  // Already completed
        "order_status": "CONFIRMED"
    }
}
```

**Action:** No gateway check performed (optimization)

**Response:**
```json
{
    "order": {
        "payment_status": "COMPLETED",  // No change
        "order_status": "CONFIRMED"     // No change
    },
    "status_updated": false  // No check performed
}
```

## Error Handling

### Gateway API Failure
```python
try:
    gateway_response = get_payment_status(str(order.id))
    # Process response...
except Exception as e:
    # Log error but don't fail the request
    print(f"Error checking payment status: {str(e)}")
    # Return order details without status update
```

**Behavior:**
- API call continues normally
- Returns current database status
- Error is logged for debugging
- User gets order details without interruption

## Frontend Integration

### JavaScript Example
```javascript
const getOrderDetails = async (orderId) => {
    try {
        const response = await fetch(`/api/common/orders/${orderId}/`, {
            headers: {
                'Authorization': `Bearer ${accessToken}`
            }
        });
        
        const data = await response.json();
        
        if (data.status_updated) {
            console.log('Order status was updated from payment gateway');
            
            // Handle status changes
            if (data.order.payment_status === 'COMPLETED') {
                showSuccessMessage('Payment completed successfully!');
                updateOrderUI(data.order);
            } else if (data.order.payment_status === 'FAILED') {
                showErrorMessage('Payment failed. Please try again.');
                showRetryPaymentOption(orderId);
            }
        }
        
        return data;
    } catch (error) {
        console.error('Error fetching order details:', error);
    }
};

// Usage
const orderData = await getOrderDetails(123);
```

### React Component Example
```jsx
const OrderDetails = ({ orderId }) => {
    const [order, setOrder] = useState(null);
    const [loading, setLoading] = useState(true);
    
    useEffect(() => {
        const fetchOrder = async () => {
            const data = await getOrderDetails(orderId);
            setOrder(data);
            setLoading(false);
            
            // Show notification if status was updated
            if (data.status_updated) {
                toast.success('Order status updated!');
            }
        };
        
        fetchOrder();
    }, [orderId]);
    
    if (loading) return <div>Loading...</div>;
    
    return (
        <div>
            <h2>Order #{order.order.id}</h2>
            <p>Status: {order.order.order_status}</p>
            <p>Payment: {order.order.payment_status}</p>
            
            {order.order.payment_status === 'PENDING' && (
                <div className="alert alert-info">
                    Payment is being processed. Status will update automatically.
                </div>
            )}
            
            {order.order.payment_status === 'FAILED' && (
                <button onClick={() => retryPayment(orderId)}>
                    Retry Payment
                </button>
            )}
        </div>
    );
};
```

## Benefits

1. **Real-time Updates**: Always shows current payment status
2. **Automatic Sync**: No manual status checking required
3. **Consistent Data**: Database always reflects gateway status
4. **Better UX**: Users see immediate status changes
5. **Error Resilient**: Graceful handling of gateway failures
6. **Performance Optimized**: Only checks pending orders
7. **Audit Trail**: Tracks when status was last checked

## Database Impact

### Additional Info Updates
```json
{
    "additional_info": {
        "last_checked": "2024-01-01T10:05:00Z",
        "gateway_response": "PaymentData(state=COMPLETED, transaction_id=TXN123)",
        "redirect_url": "https://...",
        "expire_at": "2024-01-01T11:00:00Z",
        "callback_url": "http://localhost:4200/status/123"
    }
}
```

### Performance Considerations
- Only pending orders trigger gateway calls
- Gateway errors don't block API response
- Minimal database updates (only when status changes)
- Efficient query patterns with proper indexing
