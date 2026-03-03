from .settings import *

# Minimal overrides for tests to avoid touching production DB
SECRET_KEY = 'test-secret-key'
DEBUG = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
from .settings import *

# Test settings override to ensure tests don't connect to production Supabase
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Ensure a stable SECRET_KEY for tests
SECRET_KEY = 'test-secret-key-for-ci'

# Disable debug in tests
DEBUG = False
