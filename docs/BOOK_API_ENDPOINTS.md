# Book API Endpoints

## Overview
This document describes the book management API endpoints that allow users to upload, download, and manage their EPUB books with processing status tracking.

## Authentication
All endpoints require authentication using JWT Bearer tokens:
```
Authorization: Bearer <your_jwt_token>
```

## Endpoints

### 1. Get User's Books
**GET** `/api/books/`

Get all books belonging to the authenticated user.

#### Query Parameters
- `status` (optional): Filter by processing status (`pending`, `processing`, `completed`, `failed`)

#### Response
```json
{
    "status": "success",
    "en": "Books retrieved successfully",
    "ar": "تم استرجاع الكتب بنجاح",
    "data": {
        "books": [
            {
                "book_id": "uuid",
                "title": "Book Title",
                "author": "Author Name",
                "description": "Book description",
                "processing_status": "completed",
                "file_size_mb": 2.5,
                "file_extension": ".epub",
                "created_at": "2024-01-01T12:00:00Z",
                "updated_at": "2024-01-01T12:30:00Z"
            }
        ],
        "count": 1
    }
}
```

#### Example Usage
```bash
# Get all books
curl -H "Authorization: Bearer <token>" http://localhost:8000/api/books/

# Get only completed books
curl -H "Authorization: Bearer <token>" http://localhost:8000/api/books/?status=completed
```

---

### 2. Upload Book
**POST** `/api/books/`

Upload a new EPUB book file using standard DRF ViewSet.

#### Request
- **Content-Type**: `multipart/form-data`
- **Max file size**: 50MB
- **Allowed formats**: EPUB only

#### Form Fields
- `title` (required): Book title
- `author` (optional): Book author
- `description` (optional): Book description
- `file` (required): EPUB file

#### Response
```json
{
    "status": "success",
    "en": "Book uploaded successfully",
    "ar": "تم رفع الكتاب بنجاح",
    "data": {
        "book_id": "uuid",
        "title": "Book Title",
        "author": "Author Name",
        "description": "Book description",
        "processing_status": "pending",
        "processing_error": null,
        "file_size_mb": 2.5,
        "file_extension": ".epub",
        "file_name": "book.epub",
        "created_at": "2024-01-01T12:00:00Z",
        "updated_at": "2024-01-01T12:00:00Z"
    }
}
```

#### Example Usage
```bash
curl -X POST \
  -H "Authorization: Bearer <token>" \
  -F "title=My Book" \
  -F "author=John Doe" \
  -F "description=A great book" \
  -F "file=@/path/to/book.epub" \
  http://localhost:8000/api/books/
```

---

### 3. Get Book Details
**GET** `/api/books/<book_id>/`

Get detailed information about a specific book.

#### Response
```json
{
    "status": "success",
    "en": "Book details retrieved successfully",
    "ar": "تم استرجاع تفاصيل الكتاب بنجاح",
    "data": {
        "book_id": "uuid",
        "title": "Book Title",
        "author": "Author Name",
        "description": "Book description",
        "processing_status": "completed",
        "processing_error": null,
        "file_size_mb": 2.5,
        "file_extension": ".epub",
        "file_name": "book.epub",
        "created_at": "2024-01-01T12:00:00Z",
        "updated_at": "2024-01-01T12:30:00Z"
    }
}
```

#### Example Usage
```bash
curl -H "Authorization: Bearer <token>" \
  http://localhost:8000/api/books/123e4567-e89b-12d3-a456-426614174000/
```

---

### 4. Download Book
**GET** `/api/books/<book_id>/download/`

Download the book file.

#### Response
- **Content-Type**: `application/epub+zip`
- **Content-Disposition**: `attachment; filename="book.epub"`
- **Body**: Binary file content

#### Example Usage
```bash
curl -H "Authorization: Bearer <token>" \
  -o downloaded_book.epub \
  http://localhost:8000/api/books/123e4567-e89b-12d3-a456-426614174000/download/
```

---

### 5. Get Book Processing Status
**GET** `/api/books/<book_id>/status/`

Get the current processing status of a book.

#### Response
```json
{
    "status": "success",
    "en": "Book status retrieved successfully",
    "ar": "تم استرجاع حالة الكتاب بنجاح",
    "data": {
        "book_id": "uuid",
        "title": "Book Title",
        "processing_status": "processing",
        "processing_error": null,
        "updated_at": "2024-01-01T12:15:00Z"
    }
}
```

#### Processing Status Values
- `pending`: Book uploaded, waiting to be processed
- `processing`: Book is currently being processed
- `completed`: Book processing completed successfully
- `failed`: Book processing failed (check `processing_error` for details)

#### Example Usage
```bash
curl -H "Authorization: Bearer <token>" \
  http://localhost:8000/api/books/123e4567-e89b-12d3-a456-426614174000/status/
```

---

### 6. Delete Book
**DELETE** `/api/books/<book_id>/`

Soft delete a book (marks as deleted, doesn't remove file).

#### Response
```json
{
    "status": "success",
    "en": "Book deleted successfully",
    "ar": "تم حذف الكتاب بنجاح"
}
```

#### Example Usage
```bash
curl -X DELETE \
  -H "Authorization: Bearer <token>" \
  http://localhost:8000/api/books/123e4567-e89b-12d3-a456-426614174000/
```

## Error Responses

### 400 Bad Request
```json
{
    "status": "error",
    "en": "Invalid book data",
    "ar": "بيانات الكتاب غير صحيحة",
    "errors": {
        "file": ["Only EPUB files are allowed."]
    }
}
```

### 401 Unauthorized
```json
{
    "status": "error",
    "en": "Authentication required",
    "ar": "المصادقة مطلوبة"
}
```

### 404 Not Found
```json
{
    "status": "error",
    "en": "Book not found or access denied",
    "ar": "الكتاب غير موجود أو الوصول مرفوض"
}
```

### 413 File Too Large
```json
{
    "status": "error",
    "en": "Invalid book data",
    "ar": "بيانات الكتاب غير صحيحة",
    "errors": {
        "file": ["File size too large. Maximum allowed size is 50MB. Your file is 75.5MB."]
    }
}
```

## Security Features

1. **User Isolation**: Users can only access their own books
2. **File Validation**: Only EPUB files are accepted
3. **Size Limits**: Maximum file size of 50MB
4. **Soft Deletion**: Books are marked as deleted, not physically removed
5. **Access Control**: All endpoints require authentication
6. **Error Logging**: All operations are logged for monitoring

## Processing Workflow

1. **Upload**: User uploads EPUB file → Status: `pending`
2. **Processing**: System processes the book → Status: `processing`
3. **Completion**: Processing finishes → Status: `completed` or `failed`
4. **Access**: User can download and read processed books

## File Storage

- Books are stored in: `media/books/user_{user_id}/`
- Original filename is preserved
- Files are organized by user to prevent conflicts
- Storage path: `MEDIA_ROOT/books/user_{user_id}/{filename}`
