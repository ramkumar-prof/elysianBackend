# Cookie-Based Authentication Implementation

## Overview

The authentication system now supports **automatic cookie-based authentication** alongside traditional JWT token authentication. This provides seamless user experience where browsers automatically include authentication tokens in requests.

## 🍪 Cookie Implementation

### **Cookies Set on Login/Register**

When users login or register, the system now sets **two HttpOnly cookies**:

1. **`refresh_token`** - Long-lived token for refreshing access tokens
2. **`access_token`** - Short-lived token for API authentication

### **Cookie Configuration**

```python
# Development Settings
COOKIE_SECURE = False          # Set to True in production (HTTPS only)
COOKIE_SAMESITE = 'Lax'        # Cross-site request protection
COOKIE_HTTPONLY = True         # Prevents JavaScript access (XSS protection)
COOKIE_PATH = '/'              # Available on all paths

# Token Expiration
ACCESS_TOKEN_EXPIRY = 60 * 60      # 1 hour
REFRESH_TOKEN_EXPIRY = 7 * 24 * 60 * 60  # 7 days
```

## 🔐 Authentication Flow

### **1. Login/Register Response**
```json
{
    "message": "Login successful",
    "user": {
        "mobile_number": "9999999999",
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@example.com"
    },
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Plus HTTP-Only Cookies:**
- `Set-Cookie: access_token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...; HttpOnly; Path=/; SameSite=Lax`
- `Set-Cookie: refresh_token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...; HttpOnly; Path=/; SameSite=Lax`

### **2. Automatic Authentication**

The `SessionOrJWTAuthentication` class now checks for tokens in this order:

1. **Authorization Header**: `Authorization: Bearer <token>`
2. **Access Token Cookie**: `access_token` cookie
3. **Session Authentication**: Django session
4. **Anonymous Session**: Valid session for unauthenticated users

### **3. Token Refresh**

When access token expires, frontend can call refresh endpoint:

```javascript
// Automatic refresh using cookies
const response = await fetch('/api/user/refresh/', {
    method: 'POST',
    credentials: 'include'  // Include cookies
});
```

## 🚀 Frontend Integration

### **Automatic Authentication**

```javascript
// No need to manually handle tokens!
// Cookies are automatically included in requests

// Get cart items (automatically authenticated)
const cartResponse = await fetch('/api/common/cart/', {
    credentials: 'include'  // Include cookies
});

// Add to cart (automatically authenticated)
const addResponse = await fetch('/api/common/cart/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    credentials: 'include',  // Include cookies
    body: JSON.stringify({
        product_id: 123,
        variant_id: 456,
        quantity: 2
    })
});
```

### **Hybrid Approach (Recommended)**

You can still use both cookies and manual tokens:

```javascript
// Option 1: Use cookies (automatic)
fetch('/api/common/cart/', {
    credentials: 'include'
});

// Option 2: Use manual token (for mobile apps, etc.)
fetch('/api/common/cart/', {
    headers: {
        'Authorization': `Bearer ${accessToken}`
    }
});

// Option 3: Both (redundant but safe)
fetch('/api/common/cart/', {
    headers: {
        'Authorization': `Bearer ${accessToken}`
    },
    credentials: 'include'
});
```

### **Login Implementation**

```javascript
async function login(mobileNumber, password) {
    const response = await fetch('/api/user/login/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        credentials: 'include',  // Important: Include cookies
        body: JSON.stringify({
            mobile_number: mobileNumber,
            password: password
        })
    });
    
    const data = await response.json();
    
    if (response.ok) {
        // Cookies are automatically set by browser
        // You can still store access_token for manual use if needed
        localStorage.setItem('access_token', data.access_token);
        
        // All subsequent requests will be automatically authenticated
        return data;
    } else {
        throw new Error(data.error);
    }
}
```

### **Logout Implementation**

```javascript
async function logout() {
    const response = await fetch('/api/user/logout/', {
        method: 'POST',
        credentials: 'include'  // Include cookies to clear them
    });
    
    if (response.ok) {
        // Cookies are automatically cleared
        // Clear any manually stored tokens
        localStorage.removeItem('access_token');
        
        // Redirect to login page
        window.location.href = '/login';
    }
}
```

## 🔒 Security Features

### **HttpOnly Cookies**
- ✅ **XSS Protection**: JavaScript cannot access tokens
- ✅ **Automatic Inclusion**: Browser handles token management
- ✅ **Secure Transmission**: HTTPS-only in production

### **SameSite Protection**
- ✅ **CSRF Protection**: `SameSite=Lax` prevents cross-site attacks
- ✅ **Cross-Origin Safety**: Controlled cookie sharing

### **Token Expiration**
- ✅ **Short Access Tokens**: 1-hour expiry limits exposure
- ✅ **Long Refresh Tokens**: 7-day expiry for convenience
- ✅ **Automatic Refresh**: Seamless token renewal

## 📋 API Endpoints

### **Authentication Endpoints**

| Method | Endpoint | Description | Cookies Set |
|--------|----------|-------------|-------------|
| POST | `/api/user/register/` | Register new user | ✅ Both tokens |
| POST | `/api/user/login/` | Login user | ✅ Both tokens |
| POST | `/api/user/logout/` | Logout user | ❌ Clears cookies |
| POST | `/api/user/refresh/` | Refresh access token | ✅ Both tokens |

### **Protected Endpoints**

All protected endpoints now work with cookies automatically:

| Method | Endpoint | Authentication |
|--------|----------|----------------|
| GET | `/api/common/cart/` | Cookie or Header |
| POST | `/api/common/cart/` | Cookie or Header |
| POST | `/api/common/checkout/` | Cookie or Header |
| GET | `/api/user/me/` | Cookie or Header |

## 🧪 Testing

### **Test Cookie Authentication**

```bash
# 1. Login and save cookies
curl -c cookies.txt -X POST \
     -H "Content-Type: application/json" \
     -d '{"mobile_number": "9999999999", "password": "password123"}' \
     http://localhost:8000/api/user/login/

# 2. Use cookies for authenticated request
curl -b cookies.txt \
     http://localhost:8000/api/common/cart/

# 3. Add to cart using cookies
curl -b cookies.txt -X POST \
     -H "Content-Type: application/json" \
     -d '{"product_id": 1, "variant_id": 1, "quantity": 2}' \
     http://localhost:8000/api/common/cart/
```

### **Browser DevTools**

Check cookies in browser:
1. Open DevTools → Application → Cookies
2. Look for `access_token` and `refresh_token`
3. Verify `HttpOnly` flag is set

## 🔄 Migration Guide

### **Existing Frontend Code**

**Before (Manual Token Management):**
```javascript
// Manual token handling
const token = localStorage.getItem('access_token');
fetch('/api/common/cart/', {
    headers: {
        'Authorization': `Bearer ${token}`
    }
});
```

**After (Automatic Cookie Authentication):**
```javascript
// Automatic cookie handling
fetch('/api/common/cart/', {
    credentials: 'include'  // Just add this!
});
```

### **Backward Compatibility**

- ✅ **Existing code works**: Manual token authentication still supported
- ✅ **Gradual migration**: Can migrate endpoints one by one
- ✅ **No breaking changes**: Response format unchanged

## 🌟 Benefits

### **User Experience**
- ✅ **Seamless Authentication**: No manual token management
- ✅ **Persistent Login**: Survives browser refresh
- ✅ **Automatic Renewal**: Background token refresh

### **Security**
- ✅ **XSS Protection**: HttpOnly cookies prevent token theft
- ✅ **CSRF Protection**: SameSite cookies prevent cross-site attacks
- ✅ **Secure Storage**: Browser handles secure cookie storage

### **Development**
- ✅ **Simplified Code**: Less authentication boilerplate
- ✅ **Better DX**: Automatic authentication in development
- ✅ **Mobile Ready**: Still supports manual tokens for mobile apps

## 🚀 Ready to Use

The cookie-based authentication is now live and working alongside existing token authentication. Frontend applications can immediately benefit from automatic authentication by simply adding `credentials: 'include'` to fetch requests! 🍪✨
