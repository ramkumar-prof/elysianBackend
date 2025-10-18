# Checkout API Documentation

## Checkout API

**Endpoint:** `POST /api/common/checkout/`

**Authentication:** Required (JWT Token or Session)

**Description:** Process checkout for all cart items of the user, create order, and initiate payment

### Request Parameters

```json
{
    "address_id": 456  // Required: delivery address ID (must belong to authenticated user)
}
```

### Process Flow

1. **Validate Address**: Verifies address_id belongs to authenticated user
2. **Get All Cart Items**: Retrieves all cart items for the authenticated user
3. **Calculate Total**: Calculates total amount including discounts (in paisa)
4. **Format Address**: Creates delivery address string from user's address
5. **Create Order**: Creates order entry in database with all cart items
6. **Initiate Payment**: Calls PhonePe payment gateway
7. **Store Payment Data**: Saves payment details in database
8. **Clear Cart**: Removes all processed cart items

### Response

**Success (201 Created):**
```json
{
    "success": true,
    "order_id": 123,
    "redirect_url": "https://mercury.phonepe.com/transact/...",
    "message": "Order created successfully"
}
```

**Error (400 Bad Request):**
```json
{
    "error": "address_id is required"
}
```

**Error (404 Not Found):**
```json
{
    "error": "Address not found or does not belong to user"
}
```

**Error (404 Not Found):**
```json
{
    "error": "Cart is empty"
}
```

**Error (500 Internal Server Error):**
```json
{
    "error": "Payment initiation failed",
    "details": "Error details..."
}
```

### Order Item Structure

Each item in the order contains:
```json
{
    "product": 1,
    "variant": 2,
    "quantity": 2,
    "price": 15000,  // Price in paisa (₹150.00)
    "discount": 1000,  // Discount in paisa (₹10.00)
    "product_name": "Product Name",
    "variant_size": "Medium",
    "variant_type": "Regular"
}
```

### Payment Integration

- **Gateway**: PhonePe
- **Environment**: Sandbox (development) / Production (based on DJANGO_ENV)
- **Callback URL**: `http://localhost:4200/status/{order_id}`
- **Amount**: Stored in paisa for precision

### Database Tables

**Order Table:**
- `user`: Foreign key to User
- `items`: JSON array of order items
- `order_amount`: Total amount in paisa
- `payment_status`: PENDING/COMPLETED/FAILED/REFUNDED
- `order_status`: PENDING/CONFIRMED/PREPARING/OUT_FOR_DELIVERY/DELIVERED/CANCELLED/REFUNDED
- `delivery_address`: String address
- `additional_info`: JSON field for extra data

**Payment Table:**
- `order`: Foreign key to Order
- `amount`: Amount in paisa
- `transaction_id`: Unique transaction ID
- `gateway_order_id`: PhonePe order ID
- `payment_status`: PENDING/COMPLETED/FAILED
- `payment_method`: CASH/CARD/UPI/WALLET
- `additional_info`: Contains redirect_url, expire_at, callback_url

## Additional Order APIs

### Get User Orders
**Endpoint:** `GET /api/common/orders/`
**Authentication:** Required
**Response:** List of user's orders

### Get Order Details
**Endpoint:** `GET /api/common/orders/{order_id}/`
**Authentication:** Required

**Smart Status Updates:**
- **Automatic Status Check**: If order payment status is 'PENDING', automatically checks with payment gateway for latest status
- **Real-time Updates**: Updates both order and payment records in database with latest gateway status
- **Status Mapping**: Maps gateway status to internal status (COMPLETED/FAILED/PENDING)
- **Order Status Sync**: Updates order status based on payment status (CONFIRMED for completed payments, CANCELLED for failed)

**Response:** Specific order details with associated payments, with real-time status updates

**Success (200 OK):**
```json
{
    "order": {
        "id": 123,
        "payment_status": "COMPLETED",  // Updated from gateway if was pending
        "order_status": "CONFIRMED",    // Updated based on payment status
        "order_amount": 30000,
        "delivery_address": "123 Main St, City, State - 12345",
        "items": [...],
        "created_at": "2024-01-01T10:00:00Z"
    },
    "payments": [
        {
            "id": 1,
            "payment_status": "COMPLETED",  // Updated from gateway
            "transaction_id": "TXN123456",  // Updated from gateway
            "gateway_order_id": "PG_ORDER_123",
            "amount": 30000,
            "additional_info": {
                "last_checked": "2024-01-01T10:05:00Z",  // Timestamp of last gateway check
                "gateway_response": "..."  // Latest gateway response data
            }
        }
    ],
    "status_updated": true  // Indicates if status was checked/updated from gateway
}
```

## Example Usage

```javascript
// Frontend JavaScript example
const checkoutData = {
    address_id: 456  // Required: user's address ID
};

fetch('/api/common/checkout/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + accessToken
    },
    body: JSON.stringify(checkoutData)
})
.then(response => response.json())
.then(data => {
    if (data.success) {
        // Redirect user to payment page
        window.location.href = data.redirect_url;
    } else {
        console.error('Checkout failed:', data.error);
    }
});
```

## Error Handling

- **Authentication Errors**: 401 Unauthorized
- **Validation Errors**: 400 Bad Request
- **Cart Not Found**: 404 Not Found
- **Payment Gateway Errors**: 500 Internal Server Error
- **Database Errors**: 500 Internal Server Error

## Security Features

- JWT/Session authentication required
- Address ownership validation (address must belong to authenticated user)
- Automatic cart filtering (only processes user's own cart items)
- Transaction atomicity (rollback on payment failure)
- Secure payment gateway integration
- Input validation and sanitization
