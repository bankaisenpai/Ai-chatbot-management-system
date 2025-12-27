import requests
import time
import subprocess
import sys

# Give server time if not running
time.sleep(1)

try:
    data = {'email': 'finaltest@example.com', 'password': 'mypassword', 'name': 'Final Test'}
    response = requests.post('http://localhost:8002/auth/register', json=data, timeout=3)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        print("\n✅ POST /auth/register WORKS - No 500 Error!")
        import json
        token = json.loads(response.text).get('access_token')
        print(f"✅ JWT Token received: {token[:50]}...")
    else:
        print(f"\n❌ Error {response.status_code}")
        
except Exception as e:
    print(f"❌ Connection Error: {e}")
