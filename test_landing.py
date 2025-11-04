"""Test script to check landing page."""
from app import app

with app.test_client() as client:
    try:
        response = client.get('/')
        print(f'Status Code: {response.status_code}')
        if response.status_code != 200:
            print(f'Response: {response.data.decode()}')
    except Exception as e:
        print(f'Error: {e}')
        import traceback
        traceback.print_exc()
