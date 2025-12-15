#!/usr/bin/env python
"""
Comprehensive Social Media API Test Script

This script tests all endpoints of the Social Media API including:
- Authentication endpoints (register, login, profile)
- Posts endpoints (CRUD operations)
- Comments endpoints (CRUD operations, nested under posts)
- Search functionality
- Pagination
- Permission validation

To run this script:
1. Start Django server: python manage.py runserver
2. Run this script: python comprehensive_api_test.py

Base URLs:
- Authentication: http://localhost:8000/
- Posts & Comments: http://localhost:8000/api/v1/
"""

import requests
import json
import time
from datetime import datetime

# API base URLs
AUTH_BASE_URL = "http://localhost:8000"
API_BASE_URL = "http://localhost:8000/api/v1"

class APITester:
    def __init__(self):
        self.token = None
        self.user_data = None
        self.post_id = None
        self.comment_id = None
        
    def print_test_header(self, test_name):
        print(f"\n{'='*60}")
        print(f"Testing: {test_name}")
        print(f"Time: {datetime.now().isoformat()}")
        print('='*60)
    
    def print_response(self, response, title="Response"):
        print(f"\n{title}:")
        print(f"Status Code: {response.status_code}")
        try:
            print(f"Body: {json.dumps(response.json(), indent=2)}")
        except:
            print(f"Body: {response.text}")
    
    def make_request(self, method, url, data=None, headers=None, expected_status=None):
        """Make HTTP request and handle common errors"""
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers)
            elif method.upper() == 'POST':
                response = requests.post(url, json=data, headers=headers)
            elif method.upper() == 'PUT':
                response = requests.put(url, json=data, headers=headers)
            elif method.upper() == 'PATCH':
                response = requests.patch(url, json=data, headers=headers)
            elif method.upper() == 'DELETE':
                response = requests.delete(url, headers=headers)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            if expected_status and response.status_code != expected_status:
                print(f"  Expected status {expected_status}, got {response.status_code}")
            
            return response
            
        except requests.exceptions.RequestException as e:
            print(f" Request failed: {e}")
            return None
    
    def test_user_registration(self):
        """Test user registration endpoint"""
        self.print_test_header("User Registration")
        
        url = f"{AUTH_BASE_URL}/register/"
        data = {
            "username": "testuser_api",
            "email": "testapi@example.com",
            "password": "testpass123",
            "bio": "This is a test user for API validation"
        }
        
        response = self.make_request('POST', url, data=data)
        if response and response.status_code == 201:
            self.token = response.json().get('token')
            self.user_data = response.json().get('user')
            print(" Registration successful!")
            self.print_response(response)
            return True
        else:
            print(" Registration failed!")
            if response:
                self.print_response(response)
            return False
    
    def test_user_login(self):
        """Test user login endpoint"""
        self.print_test_header("User Login")
        
        url = f"{AUTH_BASE_URL}/login/"
        data = {
            "username": "testuser_api",
            "password": "testpass123"
        }
        
        response = self.make_request('POST', url, data=data)
        if response and response.status_code == 200:
            self.token = response.json().get('token')
            self.user_data = response.json().get('user')
            print(" Login successful!")
            self.print_response(response)
            return True
        else:
            print(" Login failed!")
            if response:
                self.print_response(response)
            return False
    
    def get_auth_headers(self):
        """Get headers with authentication token"""
        if not self.token:
            print(" No authentication token available!")
            return None
        return {"Authorization": f"Token {self.token}"}
    
    def test_profile_view(self):
        """Test profile view endpoint"""
        self.print_test_header("Profile View (GET)")
        
        url = f"{AUTH_BASE_URL}/profile/"
        headers = self.get_auth_headers()
        
        if not headers:
            return False
        
        response = self.make_request('GET', url, headers=headers)
        if response and response.status_code == 200:
            print(" Profile view successful!")
            self.print_response(response)
            return True
        else:
            print(" Profile view failed!")
            if response:
                self.print_response(response)
            return False
    
    def test_profile_update(self):
        """Test profile update endpoint"""
        self.print_test_header("Profile Update (PATCH)")
        
        url = f"{AUTH_BASE_URL}/profile/"
        headers = self.get_auth_headers()
        
        if not headers:
            return False
        
        data = {
            "bio": "Updated bio content via API test"
        }
        
        response = self.make_request('PATCH', url, data=data, headers=headers)
        if response and response.status_code == 200:
            print(" Profile update successful!")
            self.print_response(response)
            return True
        else:
            print(" Profile update failed!")
            if response:
                self.print_response(response)
            return False
    
    def test_posts_list_authenticated(self):
        """Test authenticated posts list"""
        self.print_test_header("Posts List (Authenticated)")
        
        url = f"{API_BASE_URL}/posts/"
        headers = self.get_auth_headers()
        
        if not headers:
            return False
        
        response = self.make_request('GET', url, headers=headers)
        if response and response.status_code == 200:
            print(" Posts list (authenticated) successful!")
            self.print_response(response)
            return True
        else:
            print(" Posts list (authenticated) failed!")
            if response:
                self.print_response(response)
            return False
    
    def test_posts_list_unauthenticated(self):
        """Test unauthenticated posts list"""
        self.print_test_header("Posts List (Unauthenticated)")
        
        url = f"{API_BASE_URL}/posts/"
        
        response = self.make_request('GET', url)
        if response and response.status_code == 200:
            print(" Posts list (unauthenticated) successful!")
            self.print_response(response)
            return True
        else:
            print(" Posts list (unauthenticated) failed!")
            if response:
                self.print_response(response)
            return False
    
    def test_create_post(self):
        """Test post creation"""
        self.print_test_header("Create Post")
        
        url = f"{API_BASE_URL}/posts/"
        headers = self.get_auth_headers()
        
        if not headers:
            return False
        
        data = {
            "title": "Test Post from API",
            "content": "This is a test post created by the API test script."
        }
        
        response = self.make_request('POST', url, data=data, headers=headers, expected_status=201)
        if response and response.status_code == 201:
            print(" Post creation successful!")
            self.post_id = response.json().get('id')
            self.print_response(response)
            return True
        else:
            print(" Post creation failed!")
            if response:
                self.print_response(response)
            return False
    
    def test_get_post(self):
        """Test getting specific post"""
        self.print_test_header("Get Specific Post")
        
        if not self.post_id:
            print(" No post ID available!")
            return False
        
        url = f"{API_BASE_URL}/posts/{self.post_id}/"
        
        response = self.make_request('GET', url)
        if response and response.status_code == 200:
            print(" Get post successful!")
            self.print_response(response)
            return True
        else:
            print(" Get post failed!")
            if response:
                self.print_response(response)
            return False
    
    def test_update_post(self):
        """Test post update"""
        self.print_test_header("Update Post")
        
        if not self.post_id:
            print(" No post ID available!")
            return False
        
        url = f"{API_BASE_URL}/posts/{self.post_id}/"
        headers = self.get_auth_headers()
        
        if not headers:
            return False
        
        data = {
            "title": "Updated Test Post Title",
            "content": "This is the updated content of the test post."
        }
        
        response = self.make_request('PUT', url, data=data, headers=headers)
        if response and response.status_code == 200:
            print(" Post update successful!")
            self.print_response(response)
            return True
        else:
            print(" Post update failed!")
            if response:
                self.print_response(response)
            return False
    
    def test_partial_update_post(self):
        """Test partial post update"""
        self.print_test_header("Partial Update Post")
        
        if not self.post_id:
            print(" No post ID available!")
            return False
        
        url = f"{API_BASE_URL}/posts/{self.post_id}/"
        headers = self.get_auth_headers()
        
        if not headers:
            return False
        
        data = {
            "title": "Partially Updated Title"
        }
        
        response = self.make_request('PATCH', url, data=data, headers=headers)
        if response and response.status_code == 200:
            print(" Partial post update successful!")
            self.print_response(response)
            return True
        else:
            print(" Partial post update failed!")
            if response:
                self.print_response(response)
            return False
    
    def test_posts_search(self):
        """Test posts search functionality"""
        self.print_test_header("Posts Search")
        
        url = f"{API_BASE_URL}/posts/?search=Updated"
        
        response = self.make_request('GET', url)
        if response and response.status_code == 200:
            print(" Posts search successful!")
            self.print_response(response)
            return True
        else:
            print(" Posts search failed!")
            if response:
                self.print_response(response)
            return False
    
    def test_posts_pagination(self):
        """Test posts pagination"""
        self.print_test_header("Posts Pagination")
        
        url = f"{API_BASE_URL}/posts/?page_size=5"
        
        response = self.make_request('GET', url)
        if response and response.status_code == 200:
            print(" Posts pagination successful!")
            self.print_response(response)
            return True
        else:
            print(" Posts pagination failed!")
            if response:
                self.print_response(response)
            return False
    
    def test_create_comment(self):
        """Test comment creation"""
        self.print_test_header("Create Comment")
        
        if not self.post_id:
            print(" No post ID available!")
            return False
        
        url = f"{API_BASE_URL}/posts/{self.post_id}/comments/"
        headers = self.get_auth_headers()
        
        if not headers:
            return False
        
        data = {
            "content": "This is a test comment on the test post."
        }
        
        response = self.make_request('POST', url, data=data, headers=headers, expected_status=201)
        if response and response.status_code == 201:
            print(" Comment creation successful!")
            self.comment_id = response.json().get('id')
            self.print_response(response)
            return True
        else:
            print(" Comment creation failed!")
            if response:
                self.print_response(response)
            return False
    
    def test_get_comments_list(self):
        """Test getting comments list for a post"""
        self.print_test_header("Get Comments List")
        
        if not self.post_id:
            print(" No post ID available!")
            return False
        
        url = f"{API_BASE_URL}/posts/{self.post_id}/comments/"
        
        response = self.make_request('GET', url)
        if response and response.status_code == 200:
            print(" Comments list successful!")
            self.print_response(response)
            return True
        else:
            print(" Comments list failed!")
            if response:
                self.print_response(response)
            return False
    
    def test_get_comment(self):
        """Test getting specific comment"""
        self.print_test_header("Get Specific Comment")
        
        if not self.comment_id or not self.post_id:
            print(" No comment ID or post ID available!")
            return False
        
        url = f"{API_BASE_URL}/posts/{self.post_id}/comments/{self.comment_id}/"
        
        response = self.make_request('GET', url)
        if response and response.status_code == 200:
            print(" Get comment successful!")
            self.print_response(response)
            return True
        else:
            print(" Get comment failed!")
            if response:
                self.print_response(response)
            return False
    
    def test_update_comment(self):
        """Test comment update"""
        self.print_test_header("Update Comment")
        
        if not self.comment_id or not self.post_id:
            print(" No comment ID or post ID available!")
            return False
        
        url = f"{API_BASE_URL}/posts/{self.post_id}/comments/{self.comment_id}/"
        headers = self.get_auth_headers()
        
        if not headers:
            return False
        
        data = {
            "content": "This is the updated comment content."
        }
        
        response = self.make_request('PUT', url, data=data, headers=headers)
        if response and response.status_code == 200:
            print(" Comment update successful!")
            self.print_response(response)
            return True
        else:
            print(" Comment update failed!")
            if response:
                self.print_response(response)
            return False
    
    def test_partial_update_comment(self):
        """Test partial comment update"""
        self.print_test_header("Partial Update Comment")
        
        if not self.comment_id or not self.post_id:
            print(" No comment ID or post ID available!")
            return False
        
        url = f"{API_BASE_URL}/posts/{self.post_id}/comments/{self.comment_id}/"
        headers = self.get_auth_headers()
        
        if not headers:
            return False
        
        data = {
            "content": "This is a partial update to the comment."
        }
        
        response = self.make_request('PATCH', url, data=data, headers=headers)
        if response and response.status_code == 200:
            print(" Partial comment update successful!")
            self.print_response(response)
            return True
        else:
            print(" Partial comment update failed!")
            if response:
                self.print_response(response)
            return False
    
    def test_comments_pagination(self):
        """Test comments pagination"""
        self.print_test_header("Comments Pagination")
        
        if not self.post_id:
            print(" No post ID available!")
            return False
        
        url = f"{API_BASE_URL}/posts/{self.post_id}/comments/?page_size=5"
        
        response = self.make_request('GET', url)
        if response and response.status_code == 200:
            print(" Comments pagination successful!")
            self.print_response(response)
            return True
        else:
            print(" Comments pagination failed!")
            if response:
                self.print_response(response)
            return False
    
    def test_unauthorized_post_access(self):
        """Test unauthorized post access (should fail)"""
        self.print_test_header("Unauthorized Post Access")
        
        if not self.post_id:
            print(" No post ID available!")
            return False
        
        # Try to update without authentication
        url = f"{API_BASE_URL}/posts/{self.post_id}/"
        data = {
            "title": "Should Not Work"
        }
        
        response = self.make_request('PATCH', url, data=data)
        if response and response.status_code == 401:
            print(" Correctly blocked unauthorized access!")
            self.print_response(response)
            return True
        else:
            print(" Security issue: Unauthorized access allowed!")
            if response:
                self.print_response(response)
            return False
    
    def test_delete_post(self):
        """Test post deletion"""
        self.print_test_header("Delete Post")
        
        if not self.post_id:
            print(" No post ID available!")
            return False
        
        url = f"{API_BASE_URL}/posts/{self.post_id}/"
        headers = self.get_auth_headers()
        
        if not headers:
            return False
        
        response = self.make_request('DELETE', url, headers=headers)
        if response and response.status_code == 204:
            print(" Post deletion successful!")
            print("Response: No content (204 status)")
            return True
        else:
            print(" Post deletion failed!")
            if response:
                self.print_response(response)
            return False
    
    def test_delete_comment(self):
        """Test comment deletion"""
        self.print_test_header("Delete Comment")
        
        if not self.comment_id or not self.post_id:
            print(" No comment ID or post ID available!")
            return False
        
        url = f"{API_BASE_URL}/posts/{self.post_id}/comments/{self.comment_id}/"
        headers = self.get_auth_headers()
        
        if not headers:
            return False
        
        response = self.make_request('DELETE', url, headers=headers)
        if response and response.status_code == 204:
            print(" Comment deletion successful!")
            print("Response: No content (204 status)")
            return True
        else:
            print(" Comment deletion failed!")
            if response:
                self.print_response(response)
            return False
    
    def run_all_tests(self):
        """Run all API tests in sequence"""
        print(" Starting Comprehensive Social Media API Test Suite")
        print(f"Base URL: {AUTH_BASE_URL}")
        print(f"API URL: {API_BASE_URL}")
        
        test_results = []
        
        # Authentication tests
        if self.test_user_registration():
            test_results.append(" User Registration")
        else:
            # Try login if registration failed
            if self.test_user_login():
                test_results.append(" User Login")
            else:
                test_results.append(" Authentication Failed")
                return test_results
        
        # Profile tests
        if self.test_profile_view():
            test_results.append(" Profile View")
        if self.test_profile_update():
            test_results.append(" Profile Update")
        
        # Posts tests
        if self.test_posts_list_unauthenticated():
            test_results.append(" Posts List (Unauthenticated)")
        if self.test_posts_list_authenticated():
            test_results.append(" Posts List (Authenticated)")
        if self.test_create_post():
            test_results.append(" Create Post")
        if self.test_get_post():
            test_results.append(" Get Post")
        if self.test_update_post():
            test_results.append(" Update Post")
        if self.test_partial_update_post():
            test_results.append(" Partial Update Post")
        if self.test_posts_search():
            test_results.append(" Posts Search")
        if self.test_posts_pagination():
            test_results.append(" Posts Pagination")
        
        # Comments tests
        if self.test_create_comment():
            test_results.append(" Create Comment")
        if self.test_get_comments_list():
            test_results.append(" Get Comments List")
        if self.test_get_comment():
            test_results.append(" Get Comment")
        if self.test_update_comment():
            test_results.append(" Update Comment")
        if self.test_partial_update_comment():
            test_results.append(" Partial Update Comment")
        if self.test_comments_pagination():
            test_results.append(" Comments Pagination")
        
        # Security tests
        if self.test_unauthorized_post_access():
            test_results.append(" Security Test (Unauthorized Access Blocked)")
        
        # Cleanup tests
        if self.test_delete_comment():
            test_results.append(" Delete Comment")
        if self.test_delete_post():
            test_results.append(" Delete Post")
        
        return test_results

def main():
    """Main test function"""
    print("="*80)
    print("🔧 SOCIAL MEDIA API COMPREHENSIVE TEST SUITE")
    print("="*80)
    print("  Make sure Django server is running on http://localhost:8000")
    print("   Start server with: python manage.py runserver")
    print("="*80)
    
    tester = APITester()
    results = tester.run_all_tests()
    
    print("\n" + "="*80)
    print(" TEST RESULTS SUMMARY")
    print("="*80)
    
    for result in results:
        print(result)
    
    passed = len([r for r in results if r.startswith("")])
    failed = len([r for r in results if r.startswith("")])
    
    print(f"\n Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print(" All tests passed! API is working correctly.")
    else:
        print("  Some tests failed. Please review the output above.")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    main()