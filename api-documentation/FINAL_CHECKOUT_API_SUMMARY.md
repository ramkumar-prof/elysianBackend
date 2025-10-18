# Final Checkout API Summary

## API Endpoint
**POST** `/api/common/checkout/`

## Authentication
- **Required**: JWT Token or Session Authentication
- **User Context**: All operations are scoped to the authenticated user

## Request Format
```json
{
    "address_id": 456  // Required: User's delivery address ID
}
```

## Process Flow

### 1. Address Validation
- Verifies `address_id` belongs to authenticated user
- Returns 404 if address not found or doesn't belong to user

### 2. Cart Processing
- Fetches **ALL** cart items for the authenticated user
- Returns 404 if cart is empty
- Calculates total amount including discounts (stored in paisa)

### 3. Order Creation
- Creates order with all cart items
- Formats delivery address from user's address record
- Stores order details in database

### 4. Payment Integration
- Initiates payment via PhonePe gateway
- Uses environment-based configuration (sandbox/production)
- Callback URL: `http://localhost:4200/status/{order_id}`

### 5. Data Storage
- Stores payment details in Payment table
- Links payment to order
- Stores gateway response data

### 6. Cart Cleanup
- Removes all processed cart items
- Ensures clean state for user

## Response Format

### Success (201 Created)
```json
{
    "success": true,
    "order_id": 123,
    "redirect_url": "https://mercury.phonepe.com/transact/...",
    "message": "Order created successfully"
}
```

### Error Responses

#### Missing Address (400 Bad Request)
```json
{
    "error": "address_id is required"
}
```

#### Invalid Address (404 Not Found)
```json
{
    "error": "Address not found or does not belong to user"
}
```

#### Empty Cart (404 Not Found)
```json
{
    "error": "Cart is empty"
}
```

#### Payment Failure (500 Internal Server Error)
```json
{
    "error": "Payment initiation failed",
    "details": "Error details..."
}
```

## Database Schema

### Order Table
```sql
- id: Primary Key
- user: Foreign Key to User
- items: JSON array of cart items
- order_amount: Integer (amount in paisa)
- payment_id: String (payment reference)
- payment_status: PENDING/COMPLETED/FAILED/REFUNDED
- order_status: PENDING/CONFIRMED/PREPARING/OUT_FOR_DELIVERY/DELIVERED/CANCELLED/REFUNDED
- delivery_address: Text (formatted address string)
- additional_info: JSON (address_id, total_items)
- created_at: Timestamp
- updated_at: Timestamp
```

### Payment Table
```sql
- id: Primary Key
- order: Foreign Key to Order
- amount: Integer (amount in paisa)
- transaction_id: String (unique)
- gateway_order_id: String (PhonePe order ID)
- payment_status: PENDING/COMPLETED/FAILED
- payment_method: CASH/CARD/UPI/WALLET
- additional_info: JSON (redirect_url, expire_at, callback_url)
- created_at: Timestamp
- updated_at: Timestamp
```

## Order Items Structure
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

## Address Formatting
Address is formatted as:
`"Address, City, State - Pincode"`

Example: `"123 Main Street, Test Area, Mumbai, Maharashtra - 400001"`

## Security Features
- ✅ JWT/Session authentication required
- ✅ Address ownership validation
- ✅ Automatic user-scoped cart filtering
- ✅ Transaction atomicity (rollback on failure)
- ✅ Secure payment gateway integration
- ✅ Input validation and sanitization

## Payment Integration
- **Gateway**: PhonePe
- **Environment**: Automatic (sandbox for dev, production for prod)
- **Currency**: INR (amounts in paisa)
- **Callback**: Redirects to Angular frontend with order ID

## Frontend Integration Example
```javascript
const checkout = async (addressId) => {
    try {
        const response = await fetch('/api/common/checkout/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${accessToken}`
            },
            body: JSON.stringify({
                address_id: addressId
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Redirect to payment gateway
            window.location.href = data.redirect_url;
        } else {
            console.error('Checkout failed:', data.error);
        }
    } catch (error) {
        console.error('Network error:', error);
    }
};
```

## Key Benefits
1. **Simplified**: No cart_id needed - processes all user items
2. **Secure**: Complete ownership validation
3. **Atomic**: All-or-nothing transaction processing
4. **Integrated**: Seamless PhonePe payment flow
5. **Clean**: Automatic cart cleanup after successful order
6. **Flexible**: Environment-based configuration
