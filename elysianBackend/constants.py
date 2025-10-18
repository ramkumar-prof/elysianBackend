import os
from django.conf import settings

# Import PhonePe SDK environment enum
try:
    # For PhonePe SDK
    from phonepe.sdk.pg.env import Env
except ImportError:
    # Fallback if PhonePe SDK not installed
    class Env:
        SANDBOX = 'SANDBOX'
        PRODUCTION = 'PRODUCTION'

# Environment detection
ENVIRONMENT = os.getenv('DJANGO_ENV', 'development').lower()
IS_PRODUCTION = ENVIRONMENT == 'production'
IS_DEVELOPMENT = ENVIRONMENT == 'development'
IS_QA = ENVIRONMENT == 'qa'

# Cookie settings
REFRESH_TOKEN_COOKIE_NAME = 'refresh_token'
ACCESS_TOKEN_COOKIE_NAME = 'access_token'
SESSION_COOKIE_NAME = 'sessionid'

# Payment settings
if IS_PRODUCTION:
    CLIENT_ID = os.getenv('CLIENT_ID')
    CLIENT_SECRET = os.getenv('CLIENT_SECRET')
    CLIENT_VERSION = 1
    PAYMENT_ENV = Env.PRODUCTION
else:
    CLIENT_ID = "TEST-M23M5J1PBA7UO_25101"
    CLIENT_SECRET = "MWNlYzg3MjItNjBlOS00Nzg2LWJjYTQtYTkxZGJiNGY1Mzg0"
    CLIENT_VERSION = 1
    PAYMENT_ENV = Env.SANDBOX

# Cookie security settings
if IS_PRODUCTION:
    # Production: Read from environment variables
    COOKIE_SECURE = os.getenv('COOKIE_SECURE', 'True').lower() == 'true'
    COOKIE_SAMESITE = os.getenv('COOKIE_SAMESITE', 'Strict')
    COOKIE_HTTPONLY = os.getenv('COOKIE_HTTPONLY', 'True').lower() == 'true'
    COOKIE_PATH = os.getenv('COOKIE_PATH', '/')
else:
    # Development/QA: Use constants
    COOKIE_SECURE = False
    COOKIE_SAMESITE = 'Lax'
    COOKIE_HTTPONLY = True
    COOKIE_PATH = '/'

# Token expiration times (in seconds)
if IS_PRODUCTION:
    REFRESH_TOKEN_EXPIRY = int(os.getenv('REFRESH_TOKEN_EXPIRY', str(7 * 24 * 60 * 60)))  # 7 days default
    ACCESS_TOKEN_EXPIRY = int(os.getenv('ACCESS_TOKEN_EXPIRY', str(60 * 60)))  # 1 hour default
    SESSION_EXPIRY = int(os.getenv('SESSION_EXPIRY', str(14 * 24 * 60 * 60)))  # 14 days default
else:
    # Development/QA constants
    REFRESH_TOKEN_EXPIRY = 7 * 24 * 60 * 60  # 7 days
    ACCESS_TOKEN_EXPIRY = 60 * 60  # 1 hour
    SESSION_EXPIRY = 14 * 24 * 60 * 60  # 14 days

# CORS settings
if IS_PRODUCTION:
    CORS_ALLOWED_ORIGINS = os.getenv('CORS_ALLOWED_ORIGINS', '').split(',')
    CORS_ALLOW_CREDENTIALS = os.getenv('CORS_ALLOW_CREDENTIALS', 'True').lower() == 'true'
else:
    # Development/QA constants
    CORS_ALLOWED_ORIGINS = [
        "http://localhost:4200",
        "http://127.0.0.1:4200",
        "http://frontend:4200",  # For other frontend frameworks
        "http://127.0.0.1:3000"
    ]
    CORS_ALLOW_CREDENTIALS = True

# Database settings
if IS_PRODUCTION:
    DATABASE_URL = os.getenv('DATABASE_URL')
    DATABASE_NAME = os.getenv('DATABASE_NAME')
    DATABASE_USER = os.getenv('DATABASE_USER')
    DATABASE_PASSWORD = os.getenv('DATABASE_PASSWORD')
    DATABASE_HOST = os.getenv('DATABASE_HOST', 'localhost')
    DATABASE_PORT = os.getenv('DATABASE_PORT', '5432')
else:
    # Development/QA: Use SQLite
    DATABASE_URL = None
    DATABASE_NAME = 'db.sqlite3'
    DATABASE_USER = None
    DATABASE_PASSWORD = None
    DATABASE_HOST = None
    DATABASE_PORT = None

# API Rate limiting
if IS_PRODUCTION:
    API_RATE_LIMIT = os.getenv('API_RATE_LIMIT', '1000/hour')
    API_BURST_LIMIT = os.getenv('API_BURST_LIMIT', '100/minute')
else:
    # Development/QA: More lenient limits
    API_RATE_LIMIT = '10000/hour'
    API_BURST_LIMIT = '1000/minute'

# Email settings
if IS_PRODUCTION:
    EMAIL_BACKEND = os.getenv('EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend')
    EMAIL_HOST = os.getenv('EMAIL_HOST')
    EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
    EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True').lower() == 'true'
    EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
    EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
else:
    # Development/QA: Use console backend
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
    EMAIL_HOST = None
    EMAIL_PORT = None
    EMAIL_USE_TLS = None
    EMAIL_HOST_USER = None
    EMAIL_HOST_PASSWORD = None

# Logging levels
if IS_PRODUCTION:
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'WARNING')
elif IS_QA:
    LOG_LEVEL = 'INFO'
else:
    LOG_LEVEL = 'DEBUG'

# Cache settings
if IS_PRODUCTION:
    CACHE_BACKEND = os.getenv('CACHE_BACKEND', 'django.core.cache.backends.redis.RedisCache')
    CACHE_LOCATION = os.getenv('CACHE_LOCATION', 'redis://127.0.0.1:6379/1')
else:
    # Development/QA: Use local memory cache
    CACHE_BACKEND = 'django.core.cache.backends.locmem.LocMemCache'
    CACHE_LOCATION = 'unique-snowflake'
