import pytest
import requests
import json
from typing import Dict, Any, Optional
from datetime import datetime

class TestPostsGet:
    """Tests for GET /posts/{id}"""

    base_url = "https://jsonplaceholder.typicode.com"

    def test_get_posts(self):
        """GET /posts/{id} - Basic test"""

        # Path parametreleri için örnek değerler
        id = 1

        # Path parametrelerini URL'ye yerleştir
        url = f"{self.base_url}/posts/{id}"

        response = requests.get(url)

        # Temel doğrulamalar
        assert response.status_code in [200]

        # JSON response kontrolü
        assert response.headers.get('content-type', '').startswith('application/json')
        json_data = response.json()
        assert isinstance(json_data, (dict, list))

        # Response süresi kontrolü
        assert response.elapsed.total_seconds() < 30

        print(f"✓ GET /posts/{id} - Basic test - Status: {response.status_code}")

    def test_get_posts_missing_id(self):
        """GET /posts/{id} - Missing required parameter id"""

        # Eksik path parametresi ile test
        id = 999999
        url = f"{self.base_url}/posts/999999"

        response = requests.get(url)

        # Hata durumu doğrulaması (400, 422 veya 404)
        assert response.status_code in [400, 422, 404]

        # Response süresi kontrolü
        assert response.elapsed.total_seconds() < 30

        print(f"✓ GET /posts/{id} - Missing/Invalid parameter id - Status: {response.status_code}")
