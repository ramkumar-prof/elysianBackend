# Admin Add Menu Item API

## Overview
This document describes the new admin-only API endpoint for adding menu items to restaurants.

## Endpoint
```
POST /api/restaurant/admin/menu/add/
```

## Authentication & Authorization
- **Authentication**: JWT token required (JWTOnlyAuthentication)
- **Authorization**: Admin users only (staff or superuser)
- **Access Control**: Only users with `is_staff=True` or `is_superuser=True` can access this endpoint

## Request Format

### Headers
```
Content-Type: application/json
Authorization: Bearer <jwt_access_token>
```

### Request Body
```json
{
    "product_id": 123,
    "restaurent_id": 456,
    "is_available": true,
    "is_veg": false,
    "default_variant_id": 789
}
```

### Field Descriptions
- `product_id` (integer, required): ID of the product to add to the menu
- `restaurent_id` (integer, required): ID of the restaurant
- `is_available` (boolean, optional): Whether the menu item is available (default: true)
- `is_veg` (boolean, optional): Whether the item is vegetarian (default: false)
- `default_variant_id` (integer, optional): ID of the default variant for this menu item

## Response Format

### Success Response (201 Created)
```json
{
    "message": "Menu item added successfully",
    "menu_item": {
        "id": 123,
        "name": "Product Name",
        "description": "Product description",
        "variants": [
            {
                "variant_id": 789,
                "size": "Medium",
                "price": 299.99,
                "size_description": "Medium size description",
                "default": true
            }
        ],
        "images_url": ["image1.jpg", "image2.jpg"],
        "discount_percentage": 10.00,
        "is_available": true,
        "veg": false,
        "category": "Category Name",
        "sub_categories": ["tag1", "tag2"],
        "product_id": 123
    }
}
```

### Error Responses

#### 400 Bad Request - Validation Error
```json
{
    "error": "Validation failed",
    "details": {
        "product_id": ["Product with this ID does not exist."],
        "non_field_errors": ["This product is already in the restaurant's menu."]
    }
}
```

#### 401 Unauthorized
```json
{
    "detail": "Authentication credentials were not provided."
}
```

#### 403 Forbidden
```json
{
    "detail": "You do not have permission to perform this action."
}
```

## Validation Rules

1. **Product Existence**: The specified `product_id` must exist in the database
2. **Restaurant Existence**: The specified `restaurent_id` must exist in the database
3. **Variant Validation**: If `default_variant_id` is provided:
   - The variant must exist
   - The variant must belong to the specified product
4. **Duplicate Prevention**:
   - **Application Level**: Serializer validation prevents duplicate menu items during request processing
   - **Database Level**: Unique constraint on (restaurant, product) prevents race conditions and ensures data integrity
   - **Error Handling**: Graceful handling of both validation errors and database constraint violations
   - **User Experience**: Clear error messages indicating when a product is already in the restaurant's menu

## Example Usage

### Using curl
```bash
# Get JWT token first (admin user)
curl -X POST http://localhost:8000/api/user/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "mobile_number": "9876543210",
    "password": "admin_password"
  }'

# Add menu item
curl -X POST http://localhost:8000/api/restaurant/admin/menu/add/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <access_token>" \
  -d '{
    "product_id": 123,
    "restaurent_id": 456,
    "is_available": true,
    "is_veg": false,
    "default_variant_id": 789
  }'
```

### Using JavaScript/Fetch
```javascript
const response = await fetch('/api/restaurant/admin/menu/add/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${accessToken}`
  },
  body: JSON.stringify({
    product_id: 123,
    restaurent_id: 456,
    is_available: true,
    is_veg: false,
    default_variant_id: 789
  })
});

const result = await response.json();
```

## Implementation Details

### Files Modified/Created
- `restaurent/views.py`: Added `admin_add_menu_item` view
- `restaurent/models.py`: Added unique constraint for duplicate prevention
- `restaurent/serializers.py`: Added `AddMenuItemSerializer` with enhanced duplicate handling
- `restaurent/urls.py`: Added URL pattern for admin endpoint
- `restaurent/admin.py`: Registered `RestaurentMenu` model in Django admin
- `user/permissions.py`: Added `IsAdminUser` and other permission classes
- `Test/test_admin_add_menu_item.py`: Comprehensive test suite including duplicate prevention
- `restaurent/migrations/0002_add_unique_constraint_menu.py`: Database migration for unique constraint

### Security Features
- JWT-only authentication (no session-based access)
- Admin permission validation
- Input validation and sanitization
- Prevents duplicate menu items
- Cross-field validation for variants

### Database Changes
No database migrations required - uses existing models.

## Testing
Run the test suite:
```bash
python Test/test_admin_add_menu_item.py
```

The test covers:
- Admin user can successfully add menu items
- Regular users are denied access (403)
- Unauthenticated users are denied access (401)
- Added menu items appear in the public menu list
- Validation of duplicate menu items
- Proper error responses

## Related Endpoints
- `GET /api/restaurant/menu/` - View all menu items (public)
- `POST /api/user/login/` - Get JWT token for authentication
- Django Admin interface for manual menu management
