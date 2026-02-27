# API Test Configuration
import os

class Config:
    """Test konfigürasyonu"""
    
    BASE_URL = "https://jsonplaceholder.typicode.com"
    
    # Timeout ayarları (saniye)
    REQUEST_TIMEOUT = 30
    
    # Retry ayarları
    MAX_RETRIES = 3
    RETRY_DELAY = 1
    
    # Log ayarları
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    # Authentication (gerekirse)
    API_KEY = os.getenv('API_KEY', '')
    BEARER_TOKEN = os.getenv('BEARER_TOKEN', '')
    
    # Test verileri
    TEST_USER_EMAIL = os.getenv('TEST_USER_EMAIL', 'test@example.com')
    TEST_USER_PASSWORD = os.getenv('TEST_USER_PASSWORD', 'test123')

config = Config()
