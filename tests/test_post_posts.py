import pytest
import requests
import json
from typing import Dict, Any, Optional
from datetime import datetime

class TestPostsPost:
    """Tests for POST /posts"""

    base_url = "https://jsonplaceholder.typicode.com"

    def test_post_posts(self):
        """POST /posts - Basic test"""

        url = f"{self.base_url}/posts"

        # Request body
        payload = {
            "title": "Test Post",
            "body": "This is a test post",
            "userId": 1
}

        response = requests.post(url, json=payload)

        # Temel doğrulamalar
        assert response.status_code in [201]

        # Response süresi kontrolü
        assert response.elapsed.total_seconds() < 30

        print(f"✓ POST /posts - Basic test - Status: {response.status_code}")
