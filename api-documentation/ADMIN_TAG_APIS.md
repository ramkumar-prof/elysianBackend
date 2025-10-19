# Admin Tag Management APIs

## Overview

This document describes the admin-only APIs for managing tags in the Elysian Backend system. These APIs provide full CRUD (Create, Read, Update, Delete) operations for tags, which are used as subcategories for products.

## Authentication & Authorization

- **Authentication**: JWT token required (`Authorization: Bearer <token>`)
- **Authorization**: Admin users only (staff or superuser)
- **Base URL**: `/api/common/admin/tags/`

## Tag Management APIs

### 1. Create Tag

**Endpoint**: `POST /api/common/admin/tags/add/`

**Description**: Creates a new tag in the system.

#### Request Body
```json
{
    "name": "Spicy",
    "description": "Spicy food items",
    "type": ["food", "flavor"],
    "is_available": true
}
```

#### Required Fields
- `name`: Tag name (string, max 100 chars, unique)
- `description`: Tag description (text)
- `type`: Array of tag types (JSON array)
- `is_available`: Availability status (boolean, default: true)

#### Success Response (201 Created)
```json
{
    "message": "Tag created successfully",
    "tag": {
        "id": 123,
        "name": "Spicy",
        "description": "Spicy food items",
        "type": ["food", "flavor"],
        "is_available": true
    }
}
```

#### Error Response (400 Bad Request)
```json
{
    "error": "A tag with this name already exists"
}
```

### 2. Update Tag

**Endpoint**: `PUT /api/common/admin/tags/<tag_id>/update/` (full update)
**Endpoint**: `PATCH /api/common/admin/tags/<tag_id>/update/` (partial update)

**Description**: Updates an existing tag.

#### Request Body (PATCH example)
```json
{
    "description": "Updated description for spicy items",
    "type": ["food", "flavor", "hot"]
}
```

#### Success Response (200 OK)
```json
{
    "message": "Tag updated successfully",
    "tag": {
        "id": 123,
        "name": "Spicy",
        "description": "Updated description for spicy items",
        "type": ["food", "flavor", "hot"],
        "is_available": true
    }
}
```

### 3. Get Tag Details

**Endpoint**: `GET /api/common/admin/tags/<tag_id>/`

**Description**: Retrieves detailed information about a specific tag.

#### Success Response (200 OK)
```json
{
    "id": 123,
    "name": "Spicy",
    "description": "Spicy food items",
    "type": ["food", "flavor"],
    "is_available": true
}
```

### 4. List Tags

**Endpoint**: `GET /api/common/admin/tags/`

**Description**: Lists all tags with optional filtering.

#### Query Parameters
- `is_available`: Filter by availability (true/false)
- `search`: Search in tag name and description

#### Example Request
```
GET /api/common/admin/tags/?is_available=true&search=spicy
```

#### Success Response (200 OK)
```json
{
    "count": 15,
    "tags": [
        {
            "id": 123,
            "name": "Spicy",
            "description": "Spicy food items",
            "type": ["food", "flavor"],
            "is_available": true
        },
        {
            "id": 124,
            "name": "Mild Spicy",
            "description": "Mildly spicy food items",
            "type": ["food", "flavor"],
            "is_available": true
        }
    ]
}
```

### 5. Delete Tag

**Endpoint**: `DELETE /api/common/admin/tags/<tag_id>/delete/`

**Description**: Deletes a tag from the system.

#### Success Response (200 OK)
```json
{
    "message": "Tag \"Spicy\" deleted successfully"
}
```

#### Error Response (400 Bad Request)
```json
{
    "error": "Cannot delete tag that is used in products",
    "products_count": 5
}
```

## Data Model

### Tag Model Fields
- `id`: Auto-generated primary key
- `name`: Tag name (CharField, max_length=100, unique)
- `description`: Tag description (TextField, can be blank)
- `is_available`: Availability status (BooleanField, default=True)
- `type`: Array of tag types (JSONField, default=list)

### Validation Rules
1. **Name Uniqueness**: Tag names must be unique (case-insensitive)
2. **Type Format**: Type field must be a JSON array
3. **Deletion Protection**: Tags cannot be deleted if they are used in products' sub_category field

## Error Handling

### Common Error Responses

#### 401 Unauthorized
```json
{
    "detail": "Authentication required: Please provide valid JWT token"
}
```

#### 403 Forbidden
```json
{
    "detail": "You do not have permission to perform this action."
}
```

#### 404 Not Found
```json
{
    "detail": "Not found."
}
```

#### 400 Bad Request (Validation Error)
```json
{
    "error": "Invalid data provided",
    "details": {
        "name": ["A tag with this name already exists."],
        "type": ["Type must be a list."]
    }
}
```

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

# Create a new tag
curl -X POST http://localhost:8000/api/common/admin/tags/add/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <access_token>" \
  -d '{
    "name": "Vegetarian",
    "description": "Vegetarian food items",
    "type": ["food", "dietary"],
    "is_available": true
  }'

# List all tags
curl -X GET http://localhost:8000/api/common/admin/tags/ \
  -H "Authorization: Bearer <access_token>"

# Update a tag
curl -X PATCH http://localhost:8000/api/common/admin/tags/123/update/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <access_token>" \
  -d '{
    "description": "Updated description for vegetarian items"
  }'

# Delete a tag
curl -X DELETE http://localhost:8000/api/common/admin/tags/123/delete/ \
  -H "Authorization: Bearer <access_token>"
```

### Using JavaScript/Fetch

```javascript
// Create a new tag
const response = await fetch('/api/common/admin/tags/add/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${accessToken}`
  },
  body: JSON.stringify({
    name: 'Gluten-Free',
    description: 'Gluten-free food items',
    type: ['food', 'dietary'],
    is_available: true
  })
});

const result = await response.json();
```

## Security Features

1. **JWT Authentication**: All endpoints require valid JWT tokens
2. **Admin Authorization**: Only admin users (staff/superuser) can access these APIs
3. **Input Validation**: Comprehensive validation on all input fields
4. **SQL Injection Protection**: Django ORM provides protection
5. **CSRF Protection**: Not applicable for API endpoints with JWT
6. **Deletion Protection**: Prevents deletion of tags that are in use

## Testing

Comprehensive test suite available at `Test/test_admin_tag_apis.py`

### Test Coverage
- ✅ Tag CRUD operations
- ✅ Authentication and authorization
- ✅ Input validation
- ✅ Error handling
- ✅ Duplicate prevention
- ✅ Deletion protection

### Running Tests
```bash
cd /home/kulriya68/Elysian/elysianBackend
python Test/test_admin_tag_apis.py
```

## Related Endpoints
- `GET /api/common/categories/` - View all categories (public)
- `POST /api/user/login/` - Get JWT token for authentication
- Product admin APIs that use tags in sub_category field

## Notes
- Tags are used in the `sub_category` field of products as JSON arrays
- When deleting tags, the system checks if they are referenced in any products
- Tag names are case-insensitive for uniqueness validation
- The `type` field allows categorizing tags (e.g., dietary, flavor, cuisine)

---

**Last Updated**: 2025-10-19
**API Version**: 1.0
**Status**: ✅ **ACTIVE**
