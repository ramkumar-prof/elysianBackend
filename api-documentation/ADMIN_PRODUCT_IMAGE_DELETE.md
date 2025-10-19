# Admin Product Image Delete API

## Overview
Admin-only API endpoint to delete images from products. This API removes the image URL from the product's `image_urls` field and deletes the physical file and directory from media storage.

## Endpoint
```
DELETE /api/common/admin/products/delete-image/
```

## Authentication
- **Required**: JWT Token (Admin only)
- **Header**: `Authorization: Bearer <jwt_token>`
- **Permission**: `IsAdminUser`

## Request Format
- **Content-Type**: `application/json`

### Required Fields
| Field | Type | Description |
|-------|------|-------------|
| `product_id` | integer | ID of the product to delete image from |
| `image_url` | string | URL of the image to delete (must exist in product.image_urls) |

### Request Body Example
```json
{
    "product_id": 1,
    "image_url": "/api/common/images/products/paneer_tikka_1/a1b2c3d4/side_view.jpg"
}
```

## Response Format

### Success Response (200 OK)
```json
{
    "message": "Image deleted successfully",
    "deleted_image_url": "/api/common/images/products/paneer_tikka_1/a1b2c3d4/side_view.jpg",
    "product_name": "Paneer Tikka",
    "file_deleted": true,
    "remaining_images": 2,
    "updated_image_urls": [
        "/api/common/images/products/paneer_tikka_1/main/main.jpg",
        "/api/common/images/products/paneer_tikka_1/f7e8d9c2/top_view.png"
    ]
}
```

### Error Responses

#### 400 Bad Request - Missing Fields
```json
{
    "error": "product_id is required"
}
```

```json
{
    "error": "image_url is required"
}
```

#### 400 Bad Request - Invalid URL Format
```json
{
    "error": "Invalid image URL format"
}
```

#### 403 Forbidden - Unauthorized Access
```json
{
    "detail": "You do not have permission to perform this action."
}
```

#### 404 Not Found - Product Not Found
```json
{
    "error": "Product not found"
}
```

#### 404 Not Found - Image URL Not Found
```json
{
    "error": "Image URL not found in product images"
}
```

#### 500 Internal Server Error - File Deletion Failed
```json
{
    "error": "Failed to delete file: [error details]"
}
```

## Functionality

### What the API Does:
1. **Validates Input**: Checks for required fields and valid product ID
2. **Verifies Image URL**: Ensures the image URL exists in the product's `image_urls` array
3. **Deletes Physical File**: Removes the actual image file from the media directory
4. **Cleans Up Directories**: Removes empty directories after file deletion
5. **Updates Database**: Removes the image URL from the product's `image_urls` field
6. **Returns Status**: Provides detailed response about the deletion operation

### Directory Cleanup:
- Removes the image file from: `media/images/products/<product_name_id>/<random_folder>/<image_name>`
- Removes the random folder directory if it becomes empty
- Removes the product directory if it becomes empty (no more images)

### URL Format Expected:
The `image_url` must be in the format:
```
/api/common/images/products/<product_name_id>/<random_folder>/<image_name>
```

## Usage Examples

### Using curl

#### Delete a specific image
```bash
curl -X DELETE "http://localhost:8000/api/common/admin/products/delete-image/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": 1,
    "image_url": "/api/common/images/products/paneer_tikka_1/a1b2c3d4/side_view.jpg"
  }'
```

### Using JavaScript (fetch)
```javascript
const deleteImage = async (productId, imageUrl) => {
  const response = await fetch('/api/common/admin/products/delete-image/', {
    method: 'DELETE',
    headers: {
      'Authorization': `Bearer ${jwtToken}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      product_id: productId,
      image_url: imageUrl
    })
  });
  
  const data = await response.json();
  
  if (response.ok) {
    console.log('Image deleted:', data.deleted_image_url);
    console.log('Remaining images:', data.remaining_images);
  } else {
    console.error('Delete failed:', data.error);
  }
};

// Usage
deleteImage(1, '/api/common/images/products/paneer_tikka_1/a1b2c3d4/side_view.jpg');
```

### Using Python requests
```python
import requests

def delete_product_image(product_id, image_url, jwt_token):
    url = 'http://localhost:8000/api/common/admin/products/delete-image/'
    headers = {
        'Authorization': f'Bearer {jwt_token}',
        'Content-Type': 'application/json'
    }
    data = {
        'product_id': product_id,
        'image_url': image_url
    }
    
    response = requests.delete(url, json=data, headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        print(f"Image deleted: {result['deleted_image_url']}")
        print(f"Remaining images: {result['remaining_images']}")
        return result
    else:
        print(f"Delete failed: {response.status_code}")
        print(response.json())
        return None

# Usage
delete_product_image(1, '/api/common/images/products/paneer_tikka_1/a1b2c3d4/side_view.jpg', 'your_jwt_token')
```

## Security Notes

1. **Admin Only**: This endpoint requires admin privileges
2. **JWT Authentication**: Valid JWT token must be provided
3. **Input Validation**: All inputs are validated before processing
4. **Safe File Operations**: File deletion is handled safely with error checking
5. **Database Consistency**: Product image_urls are updated atomically

## Related APIs

- **Upload Image**: `POST /api/common/admin/products/upload-image/`
- **Get Product**: `GET /api/common/admin/products/<product_id>/`
- **Update Product**: `PUT /api/common/admin/products/<product_id>/update/`

## Notes

- The API will attempt to delete the physical file even if it doesn't exist (graceful handling)
- Empty directories are automatically cleaned up after file deletion
- The `file_deleted` field in the response indicates whether a physical file was actually removed
- Image URLs are removed from the product regardless of whether the physical file exists
- The API maintains the integrity of the `image_urls` array in the product model
