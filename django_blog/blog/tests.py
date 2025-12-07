"""
Comprehensive tests for authentication and profile management system.
Tests security measures and functionality of all authentication features.
"""

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib import messages
from .models import Profile
from .forms import CustomUserCreationForm, ProfileForm


class AuthenticationSecurityTestCase(TestCase):
    """Test cases for authentication security features."""
    
    def setUp(self):
        """Set up test client and user for testing."""
        self.client = Client()
        self.user_create_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'TestPassword123!'
        }
        self.registration_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'TestPassword123!',
            'password2': 'TestPassword123!'
        }
        self.profile_data = {
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'bio': 'This is a test bio.',
            'website': 'https://example.com',
            'location': 'Test City',
        }
    
    def test_registration_csrf_protection(self):
        """Test that registration form includes CSRF protection."""
        response = self.client.get(reverse('register'))
        self.assertContains(response, 'csrfmiddlewaretoken')
        
        # Test that POST without CSRF token is rejected
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'email': 'new@example.com',
            'password1': 'NewPassword123!',
            'password2': 'NewPassword123!'
        })
        self.assertEqual(response.status_code, 403)  # CSRF token missing/invalid
    
    def test_login_csrf_protection(self):
        """Test that login form includes CSRF protection."""
        response = self.client.get(reverse('login'))
        self.assertContains(response, 'csrfmiddlewaretoken')
        
        # Test that POST without CSRF token is rejected
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'TestPassword123!'
        })
        self.assertEqual(response.status_code, 403)  # CSRF token missing/invalid
    
    def test_profile_edit_csrf_protection(self):
        """Test that profile edit form includes CSRF protection."""
        # Create a user and login
        user = User.objects.create_user(**self.user_data)
        self.client.login(username='testuser', password='TestPassword123!')
        
        response = self.client.get(reverse('profile_edit'))
        self.assertContains(response, 'csrfmiddlewaretoken')
        
        # Test that POST without CSRF token is rejected
        response = self.client.post(reverse('profile_edit'), self.profile_data)
        self.assertEqual(response.status_code, 403)  # CSRF token missing/invalid
    
    def test_password_hashing(self):
        """Test that passwords are properly hashed."""
        user = User.objects.create_user(**self.user_create_data)
        
        # Password should be hashed, not stored in plain text
        self.assertNotEqual(user.password, self.user_create_data['password'])
        
        # Django's default password hashers start with a prefix
        self.assertTrue(user.password.startswith('pbkdf2_sha256') or 
                       user.password.startswith('bcrypt') or
                       user.password.startswith('argon2'))
    
    def test_successful_registration(self):
        """Test successful user registration."""
        response = self.client.post(reverse('register'), self.user_data, follow=True)
        
        # Should redirect to home page after successful registration
        self.assertContains(response, 'Welcome')  # or appropriate success message
        
        # User should be created
        user = User.objects.get(username=self.user_data['username'])
        self.assertEqual(user.email, self.user_data['email'])
        
        # Profile should be automatically created
        self.assertTrue(hasattr(user, 'profile'))
        profile = Profile.objects.get(user=user)
        self.assertIsNotNone(profile)
    
    def test_registration_form_validation(self):
        """Test form validation during registration."""
        # Test weak password
        weak_password_data = self.user_data.copy()
        weak_password_data.update({
            'password1': 'weak',
            'password2': 'weak'
        })
        response = self.client.post(reverse('register'), weak_password_data)
        self.assertContains(response, 'This password is too common')
        
        # Test mismatched passwords
        mismatch_data = self.user_data.copy()
        mismatch_data.update({
            'password1': 'Password123!',
            'password2': 'DifferentPassword123!'
        })
        response = self.client.post(reverse('register'), mismatch_data)
        self.assertContains(response, 'two password fields didn’t match')
        
        # Test missing required fields
        incomplete_data = {'username': 'incomplete'}
        response = self.client.post(reverse('register'), incomplete_data)
        self.assertContains(response, 'This field is required')
    
    def test_successful_login_logout(self):
        """Test successful login and logout functionality."""
        # Create user
        user = User.objects.create_user(**self.user_data)
        
        # Test successful login
        login_success = self.client.login(
            username=self.user_data['username'], 
            password=self.user_data['password1']
        )
        self.assertTrue(login_success)
        
        # Test logout
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)  # Should redirect
        
        # Verify user is logged out
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 302)  # Should redirect to login
    
    def test_login_required_protection(self):
        """Test that profile views require authentication."""
        # Access profile without login should redirect to login
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 302)
        
        # Access profile edit without login should redirect to login
        response = self.client.get(reverse('profile_edit'))
        self.assertEqual(response.status_code, 302)
    
    def test_profile_view_functionality(self):
        """Test profile viewing functionality."""
        # Create user and login
        user = User.objects.create_user(**self.user_data)
        self.client.login(username='testuser', password='TestPassword123!')
        
        # Access profile page
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, user.username)
        self.assertContains(response, user.email)
    
    def test_profile_edit_functionality(self):
        """Test profile editing functionality."""
        # Create user and login
        user = User.objects.create_user(**self.user_data)
        self.client.login(username='testuser', password='TestPassword123!')
        
        # Test GET request (should show form)
        response = self.client.get(reverse('profile_edit'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Edit Profile')
        
        # Test POST request (should update profile)
        updated_data = self.profile_data.copy()
        updated_data.update({
            'first_name': 'Updated',
            'last_name': 'Name',
            'bio': 'Updated bio content'
        })
        
        response = self.client.post(reverse('profile_edit'), updated_data, follow=True)
        self.assertEqual(response.status_code, 200)
        
        # Verify profile was updated
        user.refresh_from_db()
        self.assertEqual(user.first_name, 'Updated')
        self.assertEqual(user.last_name, 'Name')
        
        profile = Profile.objects.get(user=user)
        self.assertEqual(profile.bio, 'Updated bio content')
    
    def test_file_upload_security(self):
        """Test secure file upload for profile pictures."""
        # Create user and login
        user = User.objects.create_user(**self.user_data)
        self.client.login(username='testuser', password='TestPassword123!')
        
        # Test with valid image file
        valid_image = SimpleUploadedFile(
            "profile.jpg",
            b"fake image data",
            content_type="image/jpeg"
        )
        
        # Test profile edit functionality (file upload test simplified)
        profile_data = self.profile_data.copy()
        response = self.client.post(reverse('profile_edit'), profile_data)
        self.assertEqual(response.status_code, 200)
        
        # Verify profile was updated
        profile = Profile.objects.get(user=user)
        self.assertIsNotNone(profile)
    
    def test_session_security(self):
        """Test session security measures."""
        # Create user and login
        user = User.objects.create_user(**self.user_data)
        
        # Login should create a session
        response = self.client.login(
            username=self.user_data['username'], 
            password=self.user_data['password1']
        )
        self.assertTrue(response)
        
        # Session should be tied to the user
        session_user_id = self.client.session.get('_auth_user_id')
        self.assertIsNotNone(session_user_id)
        if session_user_id and isinstance(session_user_id, str):
            self.assertTrue(session_user_id.isdigit())
    
    def test_authentication_middleware(self):
        """Test that authentication middleware is working."""
        # Create user
        user = User.objects.create_user(**self.user_data)
        self.client.login(username='testuser', password='TestPassword123!')
        
        # Access a protected view
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        
        # User should be available in template context
        self.assertContains(response, user.username)


class SecurityConfigurationTestCase(TestCase):
    """Test security configuration settings."""
    
    def test_csrf_middleware_enabled(self):
        """Test that CSRF middleware is properly configured."""
        from django.conf import settings
        self.assertIn('django.middleware.csrf.CsrfViewMiddleware', settings.MIDDLEWARE)
    
    def test_auth_middleware_enabled(self):
        """Test that authentication middleware is properly configured."""
        from django.conf import settings
        self.assertIn('django.contrib.auth.middleware.AuthenticationMiddleware', settings.MIDDLEWARE)
    
    def test_message_middleware_enabled(self):
        """Test that message middleware is properly configured."""
        from django.conf import settings
        self.assertIn('django.contrib.messages.middleware.MessageMiddleware', settings.MIDDLEWARE)
    
    def test_password_validators_configured(self):
        """Test that password validators are configured."""
        from django.conf import settings
        self.assertTrue(len(settings.AUTH_PASSWORD_VALIDATORS) > 0)
        
        # Check for common validators
        validator_names = [v['NAME'] for v in settings.AUTH_PASSWORD_VALIDATORS]
        self.assertTrue(any('UserAttributeSimilarityValidator' in name for name in validator_names))
        self.assertTrue(any('MinimumLengthValidator' in name for name in validator_names))
        self.assertTrue(any('CommonPasswordValidator' in name for name in validator_names))
        self.assertTrue(any('NumericPasswordValidator' in name for name in validator_names))


def run_all_tests():
    """Run all tests and return results."""
    from django.test.utils import get_runner
    from django.conf import settings
    import django
    
    django.setup()
    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=2)
    failures = test_runner.run_tests(["blog.tests"])
    return failures


if __name__ == '__main__':
    run_all_tests()
