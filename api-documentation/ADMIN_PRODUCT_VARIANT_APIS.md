# Admin Product and Variant Management APIs

## Overview

This document describes the admin-only APIs for managing products and variants in the Elysian Backend system. These APIs provide full CRUD (Create, Read, Update, Delete) operations for products and their variants.

## Authentication & Authorization

- **Authentication**: JWT token required (`Authorization: Bearer <token>`)
- **Authorization**: Admin users only (staff or superuser)
- **Base URL**: `/api/common/admin/`

## Product Management APIs

### 1. Create Product

**Endpoint**: `POST /api/common/admin/products/add/`

**Description**: Creates a new product in the system.

#### Request Body
```json
{
    "name": "Product Name",
    "description": "Product description",
    "image_urls": ["http://example.com/image1.jpg", "http://example.com/image2.jpg"],
    "discount": 10.50,
    "is_available": true,
    "category": 1,
    "sub_category": ["tag1", "tag2"]
}
```

#### Required Fields
- `name`: Product name (string, max 200 chars)
- `category`: Category ID (integer)

#### Optional Fields
- `description`: Product description (text)
- `image_urls`: Array of image URLs (JSON array)
- `discount`: Discount percentage (decimal, 0-100)
- `is_available`: Availability status (boolean, default: true)
- `sub_category`: Array of subcategory tags (JSON array)

#### Success Response (201 Created)
```json
{
    "message": "Product created successfully",
    "product": {
        "id": 123,
        "name": "Product Name",
        "description": "Product description",
        "image_urls": ["http://example.com/image1.jpg"],
        "discount": "10.50",
        "is_available": true,
        "category": 1,
        "category_name": "Category Name",
        "sub_category": ["tag1", "tag2"],
        "variants": []
    }
}
```

### 2. Update Product

**Endpoint**: `PUT /api/common/admin/products/<product_id>/update/` (full update)
**Endpoint**: `PATCH /api/common/admin/products/<product_id>/update/` (partial update)

**Description**: Updates an existing product.

#### Request Body (PATCH example)
```json
{
    "name": "Updated Product Name",
    "discount": 15.00
}
```

#### Success Response (200 OK)
```json
{
    "message": "Product updated successfully",
    "product": {
        "id": 123,
        "name": "Updated Product Name",
        "discount": "15.00",
        // ... other fields
    }
}
```

### 3. Get Product Details

**Endpoint**: `GET /api/common/admin/products/<product_id>/`

**Description**: Retrieves detailed information about a specific product.

#### Success Response (200 OK)
```json
{
    "id": 123,
    "name": "Product Name",
    "description": "Product description",
    "image_urls": ["http://example.com/image1.jpg"],
    "discount": "10.50",
    "is_available": true,
    "category": 1,
    "category_name": "Category Name",
    "sub_category": ["tag1", "tag2"],
    "variants": [
        {
            "id": 456,
            "size": "Medium",
            "price": "25.99",
            "description": "Medium size",
            "is_available": true,
            "type": "size"
        }
    ]
}
```

### 4. List Products

**Endpoint**: `GET /api/common/admin/products/`

**Description**: Lists all products with optional filtering.

#### Query Parameters
- `category`: Filter by category ID
- `is_available`: Filter by availability (true/false)
- `search`: Search in product name and description

#### Example Request
```
GET /api/common/admin/products/?category=1&is_available=true&search=pizza
```

#### Success Response (200 OK)
```json
{
    "count": 25,
    "products": [
        {
            "id": 123,
            "name": "Product Name",
            // ... product details
        }
    ]
}
```

### 5. Delete Product

**Endpoint**: `DELETE /api/common/admin/products/<product_id>/delete/`

**Description**: Deletes a product and all its associated variants.

#### Success Response (200 OK)
```json
{
    "message": "Product \"Product Name\" deleted successfully",
    "details": "Also deleted 3 associated variants"
}
```

## Variant Management APIs

### 1. Create Variant

**Endpoint**: `POST /api/common/admin/variants/add/`

**Description**: Creates a new variant for a product.

#### Request Body
```json
{
    "product": 123,
    "size": "Large",
    "price": 29.99,
    "description": "Large size variant",
    "is_available": true,
    "type": "size"
}
```

#### Required Fields
- `product`: Product ID (integer)
- `size`: Variant size (string, max 100 chars)
- `price`: Variant price (decimal, > 0)
- `type`: Variant type (string, max 50 chars)

#### Optional Fields
- `description`: Variant description (text)
- `is_available`: Availability status (boolean, default: true)

#### Success Response (201 Created)
```json
{
    "message": "Variant created successfully",
    "variant": {
        "id": 456,
        "product": 123,
        "product_name": "Product Name",
        "size": "Large",
        "price": "29.99",
        "description": "Large size variant",
        "is_available": true,
        "type": "size"
    }
}
```

### 2. Update Variant

**Endpoint**: `PUT /api/common/admin/variants/<variant_id>/update/` (full update)
**Endpoint**: `PATCH /api/common/admin/variants/<variant_id>/update/` (partial update)

**Description**: Updates an existing variant.

#### Request Body (PATCH example)
```json
{
    "price": 32.99,
    "description": "Updated large size variant"
}
```

#### Success Response (200 OK)
```json
{
    "message": "Variant updated successfully",
    "variant": {
        "id": 456,
        "price": "32.99",
        "description": "Updated large size variant",
        // ... other fields
    }
}
```

### 3. Get Variant Details

**Endpoint**: `GET /api/common/admin/variants/<variant_id>/`

**Description**: Retrieves detailed information about a specific variant.

#### Success Response (200 OK)
```json
{
    "id": 456,
    "product": 123,
    "product_name": "Product Name",
    "size": "Large",
    "price": "29.99",
    "description": "Large size variant",
    "is_available": true,
    "type": "size"
}
```

### 4. List Variants

**Endpoint**: `GET /api/common/admin/variants/`

**Description**: Lists all variants with optional filtering.

#### Query Parameters
- `product`: Filter by product ID
- `is_available`: Filter by availability (true/false)
- `type`: Filter by variant type

#### Example Request
```
GET /api/common/admin/variants/?product=123&is_available=true&type=size
```

#### Success Response (200 OK)
```json
{
    "count": 5,
    "variants": [
        {
            "id": 456,
            "product": 123,
            "product_name": "Product Name",
            "size": "Large",
            "price": "29.99",
            "description": "Large size variant",
            "is_available": true,
            "type": "size"
        }
    ]
}
```

### 5. Delete Variant

**Endpoint**: `DELETE /api/common/admin/variants/<variant_id>/delete/`

**Description**: Deletes a specific variant.

#### Success Response (200 OK)
```json
{
    "message": "Variant \"Product Name - Large - size\" deleted successfully"
}
```

## Error Responses

### 400 Bad Request - Validation Error
```json
{
    "error": "Validation failed",
    "details": {
        "name": ["This field is required."],
        "discount": ["Discount must be between 0 and 100."]
    }
}
```

### 401 Unauthorized
```json
{
    "detail": "Authentication credentials were not provided."
}
```

### 403 Forbidden
```json
{
    "detail": "You do not have permission to perform this action."
}
```

### 404 Not Found
```json
{
    "detail": "Not found."
}
```

### 500 Internal Server Error
```json
{
    "error": "Failed to delete product",
    "details": "Database error message"
}
```

## Validation Rules

### Product Validation
1. **Name**: Required, max 200 characters
2. **Category**: Must exist and be available
3. **Discount**: Must be between 0 and 100
4. **Image URLs**: Must be valid JSON array
5. **Sub Category**: Must be valid JSON array

### Variant Validation
1. **Product**: Must exist and be available
2. **Price**: Must be greater than 0
3. **Size + Type Uniqueness**: Combination of product, size, and type must be unique
4. **Size**: Required, max 100 characters
5. **Type**: Required, max 50 characters

## Security Features

1. **JWT Authentication**: All endpoints require valid JWT tokens
2. **Admin Authorization**: Only admin users (staff/superuser) can access these APIs
3. **Input Validation**: Comprehensive validation on all input fields
4. **SQL Injection Protection**: Django ORM provides protection
5. **CSRF Protection**: Not applicable for API endpoints with JWT

## Rate Limiting

- No specific rate limiting implemented
- Consider implementing rate limiting for production use

## Testing

Comprehensive test suite available at `Test/test_admin_product_apis.py`

### Test Coverage
- ✅ Product CRUD operations
- ✅ Variant CRUD operations  
- ✅ Authentication and authorization
- ✅ Input validation
- ✅ Error handling
- ✅ Duplicate prevention

### Running Tests
```bash
cd /home/kulriya68/Elysian/elysianBackend
python Test/test_admin_product_apis.py
```
