# Core API client with retry, auth, and parsing logic
import os
import time
import json
import requests
from urllib.parse import urljoin

class APIClient:
    """Standardized API client with retry and auth support."""
    
    def __init__(self, base_url, api_key=None, timeout=None, retries=None):
        self.base_url = base_url
        self.api_key = api_key
        self.timeout = timeout or int(os.getenv("API_CLIENT_TIMEOUT", "30"))
        self.retries = retries or int(os.getenv("API_CLIENT_RETRIES", "3"))
        self.session = requests.Session()
        if api_key:
            self.session.headers.update({"Authorization": f"Bearer {api_key}"})
    
    def _request(self, method, path, **kwargs):
        url = urljoin(self.base_url, path)
        for attempt in range(self.retries):
            try:
                resp = self.session.request(method, url, timeout=self.timeout, **kwargs)
                resp.raise_for_status()
                return resp
            except requests.RequestException as e:
                if attempt == self.retries - 1:
                    raise
                time.sleep(2 ** attempt)
    
    def get(self, path, params=None):
        return self._request("GET", path, params=params)
    
    def post(self, path, json=None, data=None):
        return self._request("POST", path, json=json, data=data)
    
    def put(self, path, json=None):
        return self._request("PUT", path, json=json)
    
    def delete(self, path):
        return self._request("DELETE", path)