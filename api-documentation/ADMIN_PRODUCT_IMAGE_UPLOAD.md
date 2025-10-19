# Admin Product Image Upload API

## Overview
This document describes the admin-only API endpoint for uploading images to products. The API saves images to a structured directory format and updates the product's image_urls field.

## Endpoint
```
POST /api/common/admin/products/upload-image/
```

## Authentication & Authorization
- **Authentication**: JWT token required (JWTOnlyAuthentication)
- **Authorization**: Admin users only (staff or superuser)
- **Access Control**: Only users with `is_staff=True` or `is_superuser=True` can access this endpoint

## Request Format

### Headers
```
Content-Type: multipart/form-data
Authorization: Bearer <jwt_access_token>
```

### Request Body (Form Data)
```
product_id: <integer> (required)
image: <file> (required)
default: <boolean> (optional, default: false)
```

#### Field Descriptions

- **product_id**: The ID of the product to upload the image for
- **image**: The image file to upload (supported formats: .jpg, .jpeg, .png, .gif, .webp)
- **default**: If true, saves the image in "main" folder with filename "main" (e.g., "main.jpg")

## File Storage Structure

Images are saved in the following directory structure:
```
media/images/products/<product_name_id>/<folder_id>/<image_name>
```

Where:
- `<folder_id>` is "main" for default images, or a random 8-character string for other images

### Example Directory Structure
```
media/
└── images/
    └── products/
        └── paneer_tikka_1/
            ├── 1/
            │   └── main.jpg
            ├── 2/
            │   └── side_view.png
            └── 3/
                └── close_up.jpg
```

### URL Format
The API returns URLs in the format:
```
/api/common/images/products/<product_name_id>/<folder_id>/<image_name>
```

## Response Format

### Success Response (201 Created)
```json
{
    "message": "Image uploaded successfully",
    "image_url": "/api/common/images/products/paneer_tikka_1/main/main.jpg",
    "product_id": 1,
    "product_name": "Paneer Tikka",
    "is_default": true,
    "folder_id": "main",
    "total_images": 3
}
```

### Error Responses

#### 400 Bad Request - Missing product_id
```json
{
    "error": "product_id is required"
}
```

#### 400 Bad Request - Missing image file
```json
{
    "error": "image file is required"
}
```

#### 400 Bad Request - Invalid file type
```json
{
    "error": "Invalid file type. Allowed types: .jpg, .jpeg, .png, .gif, .webp"
}
```

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

#### 404 Not Found - Product not found
```json
{
    "error": "Product with id 123 not found"
}
```

#### 500 Internal Server Error
```json
{
    "error": "Failed to upload image: <error_details>"
}
```

## Usage Examples

### Upload Default Image
```bash
curl -X POST \
  http://localhost:8000/api/common/admin/products/upload-image/ \
  -H "Authorization: Bearer <jwt_token>" \
  -F "product_id=1" \
  -F "default=true" \
  -F "image=@main_product_image.jpg"
```

### Upload Additional Image
```bash
curl -X POST \
  http://localhost:8000/api/common/admin/products/upload-image/ \
  -H "Authorization: Bearer <jwt_token>" \
  -F "product_id=1" \
  -F "default=false" \
  -F "image=@side_view.png"
```

### Upload with Auto-increment
```bash
curl -X POST \
  http://localhost:8000/api/common/admin/products/upload-image/ \
  -H "Authorization: Bearer <jwt_token>" \
  -F "product_id=1" \
  -F "image=@additional_view.jpg"
```

## Image Management Logic

### Default Images
- When `default=true`, the image is saved as "main" with the original file extension
- If a main image already exists, it will be replaced in the product's image_urls array
- Only one main image per product is maintained

### Image Organization
- Default images (when `default=true`) are saved in the "main" folder
- Non-default images are saved in randomly generated 8-character folder names
- This ensures unique storage paths and prevents conflicts

### Product Image URLs Update
- The product's `image_urls` field is automatically updated with the new image URL
- Duplicate URLs are prevented
- The field maintains an array of all image URLs for the product

## File Validation
- **File Types**: Only image files with extensions .jpg, .jpeg, .png, .gif, .webp are allowed
- **File Size**: No explicit size limit (handled by Django's default settings)
- **File Name**: Original filename is preserved unless it's a default image

## Directory Creation
- Directories are created automatically if they don't exist
- Uses `os.makedirs(exist_ok=True)` to handle concurrent requests safely

## Error Handling
- Comprehensive error handling for file operations
- Validation of product existence before upload
- File type validation before processing
- Graceful handling of file system errors

## Security Considerations
- Admin-only access with JWT authentication
- File type validation to prevent malicious uploads
- Files are saved within the designated media directory structure
- No execution of uploaded files

## Integration with Frontend
The uploaded images can be accessed by the frontend using the returned image URLs:
```
GET /api/common/images/products/<product_name_id>/<folder_id>/<image_name>
```

This endpoint serves the images directly from the media directory with appropriate content types.
