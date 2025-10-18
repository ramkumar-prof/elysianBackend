# Test Files Documentation

This folder contains all test scripts for the Elysian Backend Django application. Each test file validates specific functionality and can be run independently.

## 🧪 Test Files Overview

### **Authentication & Session Management**

#### `test_secure_auth_flow.py`
- **Purpose**: Tests the complete authentication flow with JWT and session management
- **Features**: Login, token validation, session creation, logout
- **Usage**: `python Test/test_secure_auth_flow.py`

#### `test_new_auth_classes.py`
- **Purpose**: Tests custom authentication classes (SessionOrJWTAuthentication, JWTOnlyAuthentication, RefreshTokenAuthentication)
- **Features**: Multiple authentication methods, token validation
- **Usage**: `python Test/test_new_auth_classes.py`

#### `test_cookie_auth.py`
- **Purpose**: Tests cookie-based authentication with access and refresh tokens
- **Features**: Cookie setting, token extraction, automatic authentication
- **Usage**: `python Test/test_cookie_auth.py`

#### `test_cookie_constants.py`
- **Purpose**: Tests that cookie operations use constants instead of hardcoded names
- **Features**: Cookie name consistency, constants usage
- **Usage**: `python Test/test_cookie_constants.py`

#### `test_smart_session_api.py`
- **Purpose**: Tests enhanced session creation with automatic token refresh
- **Features**: Session creation, token refresh fallback, smart authentication
- **Usage**: `python Test/test_smart_session_api.py`

#### `test_enhanced_session_creation.py`
- **Purpose**: Tests session creation with refresh token validation
- **Features**: Session management, token validation, fallback logic
- **Usage**: `python Test/test_enhanced_session_creation.py`

### **Logout & Session Management**

#### `test_complete_logout_flow.py`
- **Purpose**: Tests complete logout process with token blacklisting
- **Features**: Token invalidation, session cleanup, security
- **Usage**: `python Test/test_complete_logout_flow.py`

#### `test_conditional_logout.py`
- **Purpose**: Tests conditional logout behavior based on authentication state
- **Features**: Conditional logic, state management
- **Usage**: `python Test/test_conditional_logout.py`

#### `test_logout_session_creation.py`
- **Purpose**: Tests new session creation during logout process
- **Features**: Session creation on logout, seamless transition
- **Usage**: `python Test/test_logout_session_creation.py`

### **Cart Management**

#### `test_cart_api.py`
- **Purpose**: Tests basic cart API functionality
- **Features**: Add to cart, get cart, cart operations
- **Usage**: `python Test/test_cart_api.py`

#### `test_cart_restructure.py`
- **Purpose**: Tests cart system restructuring with proper ForeignKey relationships
- **Features**: Cart-CartItem relationships, database integrity
- **Usage**: `python Test/test_cart_restructure.py`

#### `test_cart_quantity_management.py`
- **Purpose**: Tests cart quantity management including item removal (quantity = 0)
- **Features**: Add items, update quantities, remove items, validation
- **Usage**: `python Test/test_cart_quantity_management.py`

#### `test_unified_cart_responses.py`
- **Purpose**: Tests unified response format between GET and POST cart endpoints
- **Features**: Response consistency, format validation, API standardization
- **Usage**: `python Test/test_unified_cart_responses.py`

### **Menu & Restaurant**

#### `test_menu_to_cart_flow.py`
- **Purpose**: Tests complete flow from menu display to cart operations
- **Features**: Menu API, variant IDs, cart integration, end-to-end flow
- **Usage**: `python Test/test_menu_to_cart_flow.py`

#### `test_initial_data_loaded.py`
- **Purpose**: Tests that initial demo data is properly loaded from fixtures
- **Features**: Fixture loading, data validation, restaurant menu setup
- **Usage**: `python Test/test_initial_data_loaded.py`

#### `test_demo_data_simple.py`
- **Purpose**: Simple test for demo data availability and structure
- **Features**: Data presence, basic validation
- **Usage**: `python Test/test_demo_data_simple.py`

### **Order & Payment**

#### `test_order_status_sync.py`
- **Purpose**: Tests order status synchronization with payment gateway
- **Features**: Payment status checking, order updates, gateway integration
- **Usage**: `python Test/test_order_status_sync.py`

### **Bug Fixes & Validation**

#### `test_address_field_fix.py`
- **Purpose**: Tests the fix for Address model field access in checkout
- **Features**: Address field validation, checkout compatibility, error prevention
- **Usage**: `python Test/test_address_field_fix.py`

## 🚀 Running Tests

### **Individual Test**
```bash
# Run a specific test (from project root directory)
python Test/test_cart_quantity_management.py
```

### **All Tests** (if you want to run multiple)
```bash
# Run all cart-related tests (from project root directory)
python Test/test_cart_api.py
python Test/test_cart_quantity_management.py
python Test/test_unified_cart_responses.py
```

### **Test Categories**
```bash
# Authentication tests (run from project root)
python Test/test_secure_auth_flow.py
python Test/test_new_auth_classes.py
python Test/test_cookie_auth.py

# Cart tests (run from project root)
python Test/test_cart_quantity_management.py
python Test/test_unified_cart_responses.py
python Test/test_menu_to_cart_flow.py

# Session tests (run from project root)
python Test/test_smart_session_api.py
python Test/test_enhanced_session_creation.py
```

### **Important**:
**All tests must be run from the project root directory** (`/home/kulriya68/Elysian/elysianBackend/`) because they need to import Django modules and access the project settings.

## 📋 Test Requirements

All tests require:
- Django environment properly configured
- Database with demo data loaded (`python manage.py loaddata common/fixtures/initial_data.json`)
- Virtual environment activated
- All dependencies installed

## 🎯 Test Coverage

These tests cover:
- ✅ **Authentication**: JWT, sessions, cookies, multiple auth methods
- ✅ **Cart Management**: CRUD operations, quantity management, response formats
- ✅ **Session Management**: Creation, validation, cleanup
- ✅ **Menu Integration**: Restaurant menu to cart flow
- ✅ **Order Processing**: Status sync, payment integration
- ✅ **Bug Fixes**: Address field access, data validation
- ✅ **API Consistency**: Unified response formats, error handling

## 📝 Notes

- All tests are designed to be **independent** and can run in any order
- Tests use **temporary data** and don't affect production
- Each test includes **comprehensive output** showing what's being tested
- Tests validate both **success and error scenarios**
- **Database state** is managed within each test (creation/cleanup)

## 🔧 Troubleshooting

If tests fail:
1. **Check Django setup**: Ensure `DJANGO_SETTINGS_MODULE` is set
2. **Verify database**: Run migrations and load fixtures
3. **Check dependencies**: Ensure all packages are installed
4. **Review output**: Tests provide detailed error information
5. **Check permissions**: Ensure proper file/directory permissions

---

**Last Updated**: 2025-10-17  
**Total Test Files**: 18  
**Coverage Areas**: Authentication, Cart, Session, Menu, Orders, Bug Fixes
