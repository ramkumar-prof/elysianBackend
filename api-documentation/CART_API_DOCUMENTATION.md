# Cart API Documentation

## Overview

The Cart API provides endpoints to manage shopping cart functionality with support for both authenticated users and session-based carts.

## Endpoints

### `GET /api/common/cart/`
Get cart items for the current user or session.

#### Authentication
- **Optional**: Works with both authenticated users and sessions
- **Headers**: `Authorization: Bearer <token>` (optional)

#### Response Format
```json
{
    "cart_items": [
        {
            "cart_item_id": 789,
            "cart_id": 123,
            "product_id": 456,
            "product_name": "Margherita Pizza",
            "variant_id": 789,
            "variant_size": "Large",
            "quantity": 2,
            "price": 15.99,
            "discount": 10.0,
            "discounted_price": 14.39,
            "item_total": 28.78
        }
    ],
    "total_items": 1,
    "total_amount": 28.78
}
```

---

### `POST /api/common/cart/`
Add item to cart or update quantity if item already exists.

#### Authentication
- **Required**: Must be authenticated
- **Headers**: `Authorization: Bearer <token>`

#### Request Body
```json
{
    "product_id": 456,
    "variant_id": 789,
    "quantity": 2
}
```

#### Parameters
- **product_id** (required): ID of the product to add
- **variant_id** (required): ID of the product variant to add  
- **quantity** (optional): Quantity to add (default: 1, must be positive integer)

#### Response Format
```json
{
    "message": "Item added to cart successfully",
    "cart_items": [
        {
            "productId": 456,
            "productName": "Margherita Pizza",
            "type": "pizza",
            "selectedVariant": [
                {
                    "variantId": 789,
                    "size": "Large",
                    "quantity": 2
                },
                {
                    "variantId": 790,
                    "size": "Medium", 
                    "quantity": 1
                }
            ]
        }
    ]
}
```

#### TypeScript Interfaces
```typescript
export interface CartItemVariantSelection {
    variantId: number;
    size: string;
    quantity: number;
}

export interface CartItem {
    productId: number;
    productName: string;
    type: string;
    selectedVariant: CartItemVariantSelection[];
}
```

## Business Logic

### Add to Cart Process
1. **Validate Input**: Check required fields and data types
2. **Authenticate User**: Ensure user is logged in
3. **Validate Product/Variant**: Check if product and variant exist and are available
4. **Get/Create Cart**: Get existing cart or create new one for user
5. **Check Existing Item**: Look for existing cart item with same product/variant
6. **Update or Create**: 
   - If exists: Add quantity to existing item
   - If new: Create new cart item
7. **Return Formatted Response**: Group items by product with variant selections

### Response Grouping
The POST response groups cart items by product, showing all variant selections for each product:

**Database Structure:**
```
CartItem 1: Product A, Variant Large, Qty 2
CartItem 2: Product A, Variant Medium, Qty 1  
CartItem 3: Product B, Variant Small, Qty 3
```

**API Response:**
```json
[
    {
        "productId": "A",
        "productName": "Pizza",
        "type": "pizza",
        "selectedVariant": [
            {"variantId": "Large", "size": "Large", "quantity": 2},
            {"variantId": "Medium", "size": "Medium", "quantity": 1}
        ]
    },
    {
        "productId": "B", 
        "productName": "Burger",
        "type": "burger",
        "selectedVariant": [
            {"variantId": "Small", "size": "Small", "quantity": 3}
        ]
    }
]
```

## Error Responses

### 400 Bad Request
```json
{
    "error": "product_id and variant_id are required"
}
```

```json
{
    "error": "quantity must be a positive integer"
}
```

### 401 Unauthorized
```json
{
    "error": "Authentication required to add items to cart"
}
```

### 404 Not Found
```json
{
    "error": "Product not found or not available"
}
```

```json
{
    "error": "Variant not found or not available"
}
```

### 500 Internal Server Error
```json
{
    "error": "An error occurred: <error_message>"
}
```

## Usage Examples

### Frontend Integration

#### Get Cart Items
```javascript
// Get current cart items
const response = await fetch('/api/common/cart/', {
    method: 'GET',
    headers: {
        'Authorization': `Bearer ${token}` // Optional for sessions
    }
});
const cartData = await response.json();
```

#### Add Item to Cart
```javascript
// Add item to cart
const response = await fetch('/api/common/cart/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}` // Required
    },
    body: JSON.stringify({
        product_id: 456,
        variant_id: 789,
        quantity: 2
    })
});
const result = await response.json();
```

### cURL Examples

#### Get Cart Items
```bash
# For authenticated user
curl -H "Authorization: Bearer <token>" \
     http://localhost:8000/api/common/cart/

# For session (no auth header needed)
curl http://localhost:8000/api/common/cart/
```

#### Add Item to Cart
```bash
curl -X POST \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer <token>" \
     -d '{"product_id": 456, "variant_id": 789, "quantity": 2}' \
     http://localhost:8000/api/common/cart/
```

## Notes

### Session vs User Carts
- **Unauthenticated**: Cart tied to session ID
- **Authenticated**: Cart tied to user account
- **Cart Migration**: When user logs in, session cart can be merged with user cart

### Quantity Handling
- **Add Operation**: Always adds to existing quantity
- **Example**: If cart has 2 items and you POST quantity=3, result is 5 items
- **Zero/Negative**: Not allowed, returns 400 error

### Product/Variant Validation
- Only available products and variants can be added
- Checks `is_available=True` for both product and variant
- Ensures variant belongs to the specified product

### Performance Considerations
- Uses `select_related()` for efficient database queries
- Groups cart items by product to minimize response size
- Indexes on foreign keys for fast lookups
