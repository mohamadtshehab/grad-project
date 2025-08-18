# Authentication API Documentation

This document provides comprehensive documentation for the authentication API endpoints in the graduation project.

## Table of Contents

- [Overview](#overview)
- [Base URL](#base-url)
- [Authentication](#authentication)
- [Response Format](#response-format)
- [Error Handling](#error-handling)
- [Rate Limiting](#rate-limiting)
- [API Endpoints](#api-endpoints)
  - [User Registration](#user-registration)
  - [User Login](#user-login)
  - [Token Refresh](#token-refresh)
  - [User Logout](#user-logout)
  - [User Profile](#user-profile)
  - [Password Management](#password-management)
  - [Account Management](#account-management)

## Overview

The authentication system uses **JWT (JSON Web Tokens)** for stateless authentication. The API supports:

- User registration with email verification
- Login/logout functionality
- Profile management
- Password change and reset
- Account deletion
- Bilingual responses (English/Arabic)

## Base URL

```
http://localhost:8000/api/auth/
```

## Authentication

The API uses **Bearer Token Authentication** with JWT tokens:

```http
Authorization: Bearer <access_token>
```

### Token Types

- **Access Token**: Short-lived token (15 minutes) for API requests
- **Refresh Token**: Long-lived token (7 days) for obtaining new access tokens

## Response Format

All API responses follow a consistent format:

### Success Response
```json
{
  "status": "success",
  "en": "English message",
  "ar": "Arabic message",
  "data": {
    // Response data
  }
}
```

### Error Response
```json
{
  "status": "error",
  "en": "English error message",
  "ar": "Arabic error message",
  "error": "Detailed error information"
}
```

## Error Handling

### HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 429 | Too Many Requests |
| 500 | Internal Server Error |

### Common Error Messages

- **Validation Errors**: Field-specific validation messages
- **Authentication Errors**: Invalid credentials or expired tokens
- **Permission Errors**: Insufficient permissions for the requested action

## Rate Limiting

Password reset requests are rate-limited to prevent abuse:
- **Limit**: 5 requests per hour per IP address
- **Header**: `X-RateLimit-Remaining` shows remaining requests

## API Endpoints

---

## User Registration

Register a new user account.

### Endpoint
```http
POST /api/auth/register/
```

### Request Body
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "securepassword123",
  "password_confirm": "securepassword123"
}
```

### Request Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | User's full name |
| `email` | string | Yes | Valid email address |
| `password` | string | Yes | Password (minimum 6 characters) |
| `password_confirm` | string | Yes | Password confirmation |

### Status Codes

| Code | Description |
|------|-------------|
| 201 | User registered successfully |
| 400 | Bad Request - Validation errors (email already exists, password mismatch, invalid email format) |
| 500 | Internal Server Error |

### Response

**Success Response (201)**
```json
{
  "status": "success",
  "en": "User registered successfully",
  "ar": "تم تسجيل المستخدم بنجاح",
  "data": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "name": "John Doe",
    "email": "john@example.com",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  }
}
```

**Error Response (400)**
```json
{
  "status": "error",
  "en": "Email already exists",
  "ar": "البريد الإلكتروني موجود بالفعل",
  "error": {
    "email": ["User with this email already exists."]
  }
}
```

### Notes
- A welcome email is sent asynchronously after registration
- Email must be unique in the system
- Password must be at least 6 characters long

---

## User Login

Authenticate user and obtain JWT tokens.

### Endpoint
```http
POST /api/auth/login/
```

### Request Body
```json
{
  "email": "john@example.com",
  "password": "securepassword123"
}
```

### Request Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `email` | string | Yes | User's email address |
| `password` | string | Yes | User's password |

### Status Codes

| Code | Description |
|------|-------------|
| 200 | Login successful |
| 400 | Bad Request - Missing fields or validation errors |
| 401 | Unauthorized - Invalid credentials |
| 500 | Internal Server Error |

### Response

**Success Response (200)**
```json
{
  "status": "success",
  "en": "Logged in successfully",
  "ar": "تم تسجيل الدخول بنجاح",
  "data": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
  }
}
```

**Error Response (401)**
```json
{
  "status": "error",
  "en": "Invalid email or password",
  "ar": "بريد إلكتروني أو كلمة مرور غير صحيحة",
  "error": "Invalid credentials"
}
```

### Token Claims
The JWT access token includes:
- `user_id`: User's UUID
- `email`: User's email
- `name`: User's name
- `exp`: Token expiration time

---

## Token Refresh

Obtain a new access token using a refresh token.

### Endpoint
```http
POST /api/auth/refresh/
```

### Request Body
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### Status Codes

| Code | Description |
|------|-------------|
| 200 | Token refreshed successfully |
| 400 | Bad Request - Missing or invalid refresh token |
| 401 | Unauthorized - Invalid or expired refresh token |
| 500 | Internal Server Error |

### Response

**Success Response (200)**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Error Response (401)**
```json
{
  "status": "error",
  "en": "Token is invalid or expired",
  "ar": "الرمز المميز غير صحيح أو منتهي الصلاحية",
  "error": "Token is blacklisted"
}
```

---

## User Logout

Logout user by blacklisting the refresh token.

### Endpoint
```http
POST /api/auth/logout/
```

### Authentication
Required: Bearer Token

### Request Body
```json
{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### Status Codes

| Code | Description |
|------|-------------|
| 200 | Logged out successfully |
| 400 | Bad Request - Missing refresh token |
| 401 | Unauthorized - Invalid access token or refresh token |
| 500 | Internal Server Error |

### Response

**Success Response (200)**
```json
{
  "status": "success",
  "en": "Logged out successfully",
  "ar": "تم تسجيل الخروج بنجاح"
}
```

**Error Response (401)**
```json
{
  "status": "error",
  "en": "Authentication credentials were not provided",
  "ar": "لم يتم توفير بيانات الاعتماد للمصادقة",
  "error": "Authentication required"
}
```

---

## User Profile

### Get Profile

Retrieve the current user's profile information.

#### Endpoint
```http
GET /api/auth/profile/
```

#### Authentication
Required: Bearer Token

#### Status Codes

| Code | Description |
|------|-------------|
| 200 | Profile retrieved successfully |
| 401 | Unauthorized - Invalid or missing access token |
| 500 | Internal Server Error |

#### Response

**Success Response (200)**
```json
{
  "status": "success",
  "en": "Profile retrieved successfully",
  "ar": "تم استرجاع الملف الشخصي بنجاح",
  "data": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "name": "John Doe",
    "email": "john@example.com",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  }
}
```

### Update Profile

Update the current user's profile information.

#### Endpoint
```http
PUT /api/auth/profile/
```

#### Authentication
Required: Bearer Token

#### Request Body
```json
{
  "name": "John Smith",
  "email": "johnsmith@example.com"
}
```

#### Request Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | No | User's full name |
| `email` | string | No | User's email address |

#### Status Codes

| Code | Description |
|------|-------------|
| 200 | Profile updated successfully |
| 400 | Bad Request - Validation errors (invalid email format, email already exists) |
| 401 | Unauthorized - Invalid or missing access token |
| 500 | Internal Server Error |

#### Response

**Success Response (200)**
```json
{
  "status": "success",
  "en": "Profile updated successfully",
  "ar": "تم تحديث الملف الشخصي بنجاح",
  "data": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "name": "John Smith",
    "email": "johnsmith@example.com",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T11:45:00Z"
  }
}
```

**Error Response (400)**
```json
{
  "status": "error",
  "en": "Email already exists",
  "ar": "البريد الإلكتروني موجود بالفعل",
  "error": {
    "email": ["User with this email already exists."]
  }
}
```

---

## Password Management

### Change Password

Change the current user's password.

#### Endpoint
```http
POST /api/auth/password/change/
```

#### Authentication
Required: Bearer Token

#### Request Body
```json
{
  "old_password": "currentpassword123",
  "new_password": "newpassword456",
  "new_password_confirm": "newpassword456"
}
```

#### Request Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `old_password` | string | Yes | Current password |
| `new_password` | string | Yes | New password (minimum 6 characters) |
| `new_password_confirm` | string | Yes | New password confirmation |

#### Status Codes

| Code | Description |
|------|-------------|
| 200 | Password changed successfully |
| 400 | Bad Request - Validation errors (password mismatch, weak password) |
| 401 | Unauthorized - Invalid access token or incorrect old password |
| 500 | Internal Server Error |

#### Response

**Success Response (200)**
```json
{
  "status": "success",
  "en": "Password changed successfully",
  "ar": "تم تغيير كلمة المرور بنجاح"
}
```

**Error Response (401)**
```json
{
  "status": "error",
  "en": "Old password is incorrect",
  "ar": "كلمة المرور القديمة غير صحيحة",
  "error": "Invalid old password"
}
```

### Request Password Reset

Request a password reset code to be sent via email.

#### Endpoint
```http
POST /api/auth/password/reset/
```

#### Rate Limiting
5 requests per hour per IP address

#### Request Body
```json
{
  "email": "john@example.com"
}
```

#### Status Codes

| Code | Description |
|------|-------------|
| 200 | Reset code request processed successfully |
| 400 | Bad Request - Missing or invalid email |
| 429 | Too Many Requests - Rate limit exceeded (5 requests per hour) |
| 500 | Internal Server Error |

#### Response

**Success Response (200)**
```json
{
  "status": "success",
  "en": "Password reset code is being sent to your email",
  "ar": "يتم إرسال رمز إعادة تعيين كلمة المرور إلى بريدك الإلكتروني",
  "message": "A 6-digit code is being sent to john@example.com",
  "task_id": "celery-task-id-here"
}
```

**Error Response (429)**
```json
{
  "status": "error",
  "en": "Too many password reset requests. Please try again later",
  "ar": "طلبات إعادة تعيين كلمة المرور كثيرة جداً. يرجى المحاولة مرة أخرى لاحقاً",
  "error": "Rate limit exceeded"
}
```

#### Notes
- Returns success even if email doesn't exist (security measure)
- Reset code expires after 1 hour
- Email is sent asynchronously using Celery
- Previous unused codes are invalidated when a new one is generated

### Confirm Password Reset

Reset password using the code received via email.

#### Endpoint
```http
POST /api/auth/password/reset/confirm/
```

#### Request Body
```json
{
  "email": "john@example.com",
  "code": "123456",
  "new_password": "newpassword123",
  "new_password_confirm": "newpassword123"
}
```

#### Request Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `email` | string | Yes | User's email address |
| `code` | string | Yes | 6-digit reset code |
| `new_password` | string | Yes | New password (minimum 6 characters) |
| `new_password_confirm` | string | Yes | New password confirmation |

#### Status Codes

| Code | Description |
|------|-------------|
| 200 | Password reset successful |
| 400 | Bad Request - Validation errors (invalid code, password mismatch, weak password) |
| 404 | Not Found - User with email does not exist |
| 500 | Internal Server Error |

#### Response

**Success Response (200)**
```json
{
  "status": "success",
  "en": "Password reset successful",
  "ar": "تم إعادة تعيين كلمة المرور بنجاح",
  "message": "You can now login with your new password"
}
```

#### Error Responses

**Invalid or Expired Code**
```json
{
  "status": "error",
  "en": "Reset code has expired or is invalid",
  "ar": "رمز إعادة التعيين منتهي الصلاحية أو غير صحيح"
}
```

**User Not Found**
```json
{
  "status": "error",
  "en": "User with this email does not exist",
  "ar": "لا يوجد مستخدم بهذا البريد الإلكتروني"
}
```

---

## Account Management

### Delete Account

Permanently delete the user's account.

#### Endpoint
```http
DELETE /api/auth/account/
```

#### Authentication
Required: Bearer Token

#### Request Body
```json
{
  "password": "currentpassword123"
}
```

#### Request Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `password` | string | Yes | Current password for confirmation |

#### Status Codes

| Code | Description |
|------|-------------|
| 200 | Account deleted successfully |
| 400 | Bad Request - Missing password or validation errors |
| 401 | Unauthorized - Invalid access token or incorrect password |
| 500 | Internal Server Error |

#### Response

**Success Response (200)**
```json
{
  "status": "success",
  "en": "Account deleted successfully",
  "ar": "تم حذف الحساب بنجاح"
}
```

**Error Response (401)**
```json
{
  "status": "error",
  "en": "Password is incorrect",
  "ar": "كلمة المرور غير صحيحة",
  "error": "Invalid password"
}
```

#### Notes
- This action is irreversible
- All user data including books and characters will be deleted
- User must provide current password for confirmation

---

## Example Usage

### JavaScript/Fetch Example

```javascript
// Registration
const registerUser = async (userData) => {
  const response = await fetch('/api/auth/register/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(userData)
  });
  return response.json();
};

// Login
const loginUser = async (credentials) => {
  const response = await fetch('/api/auth/login/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(credentials)
  });
  const data = await response.json();
  
  if (data.status === 'success') {
    // Store tokens
    localStorage.setItem('access_token', data.data.access);
    localStorage.setItem('refresh_token', data.data.refresh);
  }
  
  return data;
};

// Authenticated request
const getProfile = async () => {
  const token = localStorage.getItem('access_token');
  const response = await fetch('/api/auth/profile/', {
    headers: {
      'Authorization': `Bearer ${token}`,
    }
  });
  return response.json();
};
```

### cURL Examples

```bash
# Register a new user
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "password": "securepassword123",
    "password_confirm": "securepassword123"
  }'

# Login
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "securepassword123"
  }'

# Get profile (replace TOKEN with actual access token)
curl -X GET http://localhost:8000/api/auth/profile/ \
  -H "Authorization: Bearer TOKEN"

# Change password
curl -X POST http://localhost:8000/api/auth/password/change/ \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "old_password": "securepassword123",
    "new_password": "newsecurepassword456",
    "new_password_confirm": "newsecurepassword456"
  }'
```

---

## Security Considerations

1. **HTTPS Only**: Always use HTTPS in production
2. **Token Storage**: Store tokens securely (avoid localStorage for sensitive apps)
3. **Token Refresh**: Implement automatic token refresh logic
4. **Rate Limiting**: Password reset requests are rate-limited
5. **Email Verification**: Welcome emails are sent for new registrations
6. **Password Strength**: Minimum 6 characters required
7. **Account Security**: Password required for account deletion

---

## Troubleshooting

### Common Issues

1. **Token Expired**: Use refresh token to get a new access token
2. **Invalid Credentials**: Check email and password
3. **Rate Limited**: Wait before making more password reset requests
4. **Email Not Received**: Check spam folder, verify email address
5. **CORS Issues**: Ensure proper CORS configuration for frontend

### Debug Headers

Include these headers for debugging:
```http
X-Request-ID: unique-request-id
X-Client-Version: 1.0.0
```

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2024-01-15 | Initial API documentation |

---

For additional support or questions, please refer to the project's main documentation or contact the development team.
