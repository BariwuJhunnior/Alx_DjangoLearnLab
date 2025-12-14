#!/usr/bin/env python
"""
Social Media API Test Script

This script demonstrates how to test the Social Media API endpoints once dependencies are installed.

To run this script:
1. Install dependencies: pip install django djangorestframework
2. Run migrations: python manage.py migrate
3. Run the server: python manage.py runserver
4. Execute this script to test the API endpoints

Test endpoints:
- POST /register/ - User registration
- POST /login/ - User login (returns token + user data)
- GET/PUT /profile/ - User profile management (requires token)
"""

import requests
import json

# API base URL
BASE_URL = "http://localhost:8000"

def test_user_registration():
    """Test user registration endpoint"""
    print("Testing User Registration...")
    
    url = f"{BASE_URL}/register/"
    data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123",
        "bio": "This is a test user bio"
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.json().get('token')
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_user_login(username="testuser", password="testpass123"):
    """Test user login endpoint"""
    print("\nTesting User Login...")
    
    url = f"{BASE_URL}/login/"
    data = {
        "username": username,
        "password": password
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.json().get('token')
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_profile_view(token):
    """Test profile view endpoint"""
    print("\nTesting Profile View...")
    
    url = f"{BASE_URL}/profile/"
    headers = {
        "Authorization": f"Token {token}"
    }
    
    try:
        response = requests.get(url, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")

def test_profile_update(token):
    """Test profile update endpoint"""
    print("\nTesting Profile Update...")
    
    url = f"{BASE_URL}/profile/"
    headers = {
        "Authorization": f"Token {token}"
    }
    data = {
        "bio": "Updated bio content"
    }
    
    try:
        response = requests.patch(url, json=data, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")

def main():
    """Main test function"""
    print("=== Social Media API Test Suite ===\n")
    
    # Test registration (this will create a new user)
    token = test_user_registration()
    
    if token:
        print(f"\nRegistration successful! Token: {token}")
        
        # Test profile view
        test_profile_view(token)
        
        # Test profile update
        test_profile_update(token)
        
        # Test login with existing user
        login_token = test_user_login()
        
        if login_token:
            print(f"\nLogin successful! Token: {login_token}")
            test_profile_view(login_token)
    else:
        print("\nRegistration failed!")
        
        # Try login with existing user
        login_token = test_user_login()
        if login_token:
            print(f"\nLogin successful! Token: {login_token}")
            test_profile_view(login_token)

if __name__ == "__main__":
    main()