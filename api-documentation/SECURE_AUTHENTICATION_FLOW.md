# Secure Authentication Flow

## Overview

The authentication system now requires **session-based authentication** for all API endpoints except session creation. This ensures proper security where users must first establish a session before accessing any resources.

## 🔐 Authentication Flow

### **Step 1: Session Creation (Anonymous Access)**

**Only endpoint that allows anonymous access:**

```javascript
// Create session for anonymous user
const sessionResponse = await fetch('/api/common/session/', {
    method: 'GET',
    credentials: 'include'  // Important: Include cookies
});

// Session ID is automatically set as cookie
// Now user has a valid session for authentication
```

### **Step 2: User Registration (Requires Session)**

```javascript
// Register new user (requires valid session from Step 1)
const registerResponse = await fetch('/api/user/register/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    credentials: 'include',  // Include session cookie
    body: JSON.stringify({
        mobile_number: '9999999999',
        password: 'password123',
        first_name: 'John',
        last_name: 'Doe',
        email: 'john@example.com'
    })
});

// Response includes access_token AND sets cookies
const data = await registerResponse.json();
// Cookies: access_token, refresh_token automatically set
```

### **Step 3: User Login (Requires Session)**

```javascript
// Login existing user (requires valid session from Step 1)
const loginResponse = await fetch('/api/user/login/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    credentials: 'include',  // Include session cookie
    body: JSON.stringify({
        mobile_number: '9999999999',
        password: 'password123'
    })
});

// Response includes access_token AND sets cookies
const data = await loginResponse.json();
// Cookies: access_token, refresh_token automatically set
```

### **Step 4: Authenticated API Calls**

```javascript
// All subsequent API calls are automatically authenticated
// No manual token management needed!

// Get user profile
const userResponse = await fetch('/api/user/me/', {
    credentials: 'include'
});

// Get cart items
const cartResponse = await fetch('/api/common/cart/', {
    credentials: 'include'
});

// Add to cart
const addResponse = await fetch('/api/common/cart/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    credentials: 'include',
    body: JSON.stringify({
        product_id: 123,
        variant_id: 456,
        quantity: 2
    })
});
```

### **Step 5: Secure Logout**

```javascript
// Logout clears cookies AND blacklists tokens on server
const logoutResponse = await fetch('/api/user/logout/', {
    method: 'POST',
    credentials: 'include'
});

// User is completely logged out:
// - Cookies cleared from browser
// - Tokens blacklisted on server
// - Session remains valid for future logins
```

## 🛡️ Security Model

### **Authentication Requirements**

| Endpoint | Authentication Required | Anonymous Access |
|----------|------------------------|------------------|
| `/api/common/session/` | ❌ No | ✅ Yes (ONLY endpoint) |
| `/api/user/register/` | ✅ Session Required | ❌ No |
| `/api/user/login/` | ✅ Session Required | ❌ No |
| `/api/user/logout/` | ✅ Session/JWT Required | ❌ No |
| `/api/user/refresh/` | ✅ Session/JWT Required | ❌ No |
| `/api/user/me/` | ✅ Session/JWT Required | ❌ No |
| `/api/common/cart/` | ✅ Session/JWT Required | ❌ No |
| `/api/common/checkout/` | ✅ JWT Required | ❌ No |
| `/api/restaurant/menu/` | ✅ Session/JWT Required | ❌ No |
| `/api/common/categories/` | ✅ Session/JWT Required | ❌ No |

### **Authentication Hierarchy**

1. **JWT Token** (Highest Priority)
   - From `Authorization: Bearer <token>` header
   - From `access_token` cookie

2. **Session Authentication**
   - From `sessionid` cookie
   - Allows anonymous users with valid session

3. **Anonymous Session**
   - Valid session without authenticated user
   - Only for session creation endpoint

## 🔄 Complete Frontend Implementation

### **Authentication Service**

```javascript
class AuthService {
    constructor() {
        this.isInitialized = false;
    }

    // Step 1: Initialize session (call this first)
    async initializeSession() {
        if (this.isInitialized) return;
        
        try {
            const response = await fetch('/api/common/session/', {
                method: 'GET',
                credentials: 'include'
            });
            
            if (response.ok) {
                this.isInitialized = true;
                console.log('Session initialized');
            } else {
                throw new Error('Failed to initialize session');
            }
        } catch (error) {
            console.error('Session initialization failed:', error);
            throw error;
        }
    }

    // Step 2: Register user (requires session)
    async register(userData) {
        await this.ensureSession();
        
        const response = await fetch('/api/user/register/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'include',
            body: JSON.stringify(userData)
        });
        
        if (response.ok) {
            const data = await response.json();
            // Cookies automatically set, user is now authenticated
            return data;
        } else {
            throw new Error('Registration failed');
        }
    }

    // Step 3: Login user (requires session)
    async login(mobileNumber, password) {
        await this.ensureSession();
        
        const response = await fetch('/api/user/login/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'include',
            body: JSON.stringify({
                mobile_number: mobileNumber,
                password: password
            })
        });
        
        if (response.ok) {
            const data = await response.json();
            // Cookies automatically set, user is now authenticated
            return data;
        } else {
            throw new Error('Login failed');
        }
    }

    // Step 4: Make authenticated API calls
    async apiCall(url, options = {}) {
        await this.ensureSession();
        
        return fetch(url, {
            ...options,
            credentials: 'include'  // Always include cookies
        });
    }

    // Step 5: Secure logout
    async logout() {
        const response = await fetch('/api/user/logout/', {
            method: 'POST',
            credentials: 'include'
        });
        
        if (response.ok) {
            console.log('Logged out successfully');
            // Cookies cleared, tokens blacklisted
        }
    }

    // Helper: Ensure session exists
    async ensureSession() {
        if (!this.isInitialized) {
            await this.initializeSession();
        }
    }
}

// Usage
const auth = new AuthService();

// Initialize app
async function initApp() {
    try {
        // Step 1: Always initialize session first
        await auth.initializeSession();
        
        // Now app can make authenticated calls
        console.log('App ready');
    } catch (error) {
        console.error('App initialization failed:', error);
    }
}

// Login flow
async function loginUser(mobile, password) {
    try {
        const result = await auth.login(mobile, password);
        console.log('Login successful:', result);
        
        // Now make authenticated calls
        const userProfile = await auth.apiCall('/api/user/me/');
        const cartItems = await auth.apiCall('/api/common/cart/');
        
    } catch (error) {
        console.error('Login failed:', error);
    }
}
```

## 🧪 Testing the Flow

### **Manual Testing with cURL**

```bash
# Step 1: Create session
curl -c cookies.txt -X GET \
     http://localhost:8000/api/common/session/

# Step 2: Login with session
curl -b cookies.txt -c cookies.txt -X POST \
     -H "Content-Type: application/json" \
     -d '{"mobile_number": "9999999999", "password": "password123"}' \
     http://localhost:8000/api/user/login/

# Step 3: Make authenticated calls
curl -b cookies.txt \
     http://localhost:8000/api/user/me/

curl -b cookies.txt \
     http://localhost:8000/api/common/cart/

# Step 4: Logout (clears cookies + blacklists tokens)
curl -b cookies.txt -X POST \
     http://localhost:8000/api/user/logout/
```

## 🔒 Security Benefits

### **Session-First Approach**
- ✅ **No Anonymous API Access**: All endpoints require authentication
- ✅ **Session Tracking**: Server tracks all user sessions
- ✅ **CSRF Protection**: Session-based CSRF protection
- ✅ **Rate Limiting**: Per-session rate limiting possible

### **Token Security**
- ✅ **Server-Side Blacklisting**: Tokens invalidated on logout
- ✅ **HttpOnly Cookies**: XSS protection
- ✅ **Automatic Rotation**: Refresh token rotation
- ✅ **Short Expiry**: 1-hour access tokens

### **Complete Logout**
- ✅ **Client-Side**: Cookies cleared from browser
- ✅ **Server-Side**: Tokens blacklisted in database
- ✅ **Session Preserved**: Session remains for future logins

## 🚀 Migration Guide

### **From Previous Implementation**

**Before (Insecure - AllowAny everywhere):**
```javascript
// Could access APIs without any authentication
fetch('/api/common/cart/');  // ❌ Insecure
```

**After (Secure - Session Required):**
```javascript
// Must initialize session first
await auth.initializeSession();  // ✅ Secure
await auth.login(mobile, password);
const cart = await auth.apiCall('/api/common/cart/');  // ✅ Authenticated
```

### **Key Changes**
1. **Session Creation Required**: Must call `/api/common/session/` first
2. **No Anonymous Access**: All APIs require authentication
3. **Automatic Cookies**: No manual token management
4. **Secure Logout**: Complete token invalidation

The authentication system now provides **enterprise-grade security** with session-based authentication and complete token lifecycle management! 🔐✨
