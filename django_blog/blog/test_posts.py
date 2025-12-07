"""
Simple test for blog post CRUD functionality.
"""

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Post


class BlogPostTestCase(TestCase):
    """Test basic blog post functionality."""
    
    def setUp(self):
        """Set up test client and user."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
    def test_post_creation(self):
        """Test creating a blog post."""
        # Create a post
        post = Post.objects.create(
            title='Test Post',
            content='This is test content for the blog post.',
            author=self.user,
            is_published=True
        )
        
        # Verify post was created
        self.assertEqual(Post.objects.count(), 1)
        self.assertEqual(post.title, 'Test Post')
        self.assertEqual(post.author, self.user)
        self.assertTrue(post.is_published)
        
    def test_post_list_view(self):
        """Test post list view works."""
        # Create a post
        Post.objects.create(
            title='Test Post',
            content='Test content',
            author=self.user,
            is_published=True
        )
        
        # Test GET request
        response = self.client.get(reverse('post_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Post')
        
    def test_post_detail_view(self):
        """Test post detail view works."""
        # Create a post
        post = Post.objects.create(
            title='Test Post',
            content='Test content',
            author=self.user,
            is_published=True
        )
        
        # Test GET request
        response = self.client.get(reverse('post_detail', kwargs={'pk': post.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Post')
        
    def test_create_post_requires_login(self):
        """Test that creating a post requires login."""
        response = self.client.get(reverse('post_create'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
        
    def test_create_post_authenticated(self):
        """Test creating a post when authenticated."""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.get(reverse('post_create'))
        self.assertEqual(response.status_code, 200)
        
    def test_update_requires_ownership(self):
        """Test that updating a post requires ownership."""
        # Create a post
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpass123'
        )
        post = Post.objects.create(
            title='Test Post',
            content='Test content',
            author=self.user,
            is_published=True
        )
        
        # Login as other user
        self.client.login(username='otheruser', password='otherpass123')
        
        # Try to access edit page
        response = self.client.get(reverse('post_update', kwargs={'pk': post.pk}))
        self.assertEqual(response.status_code, 403)  # Forbidden
        
    def test_own_post_can_be_updated(self):
        """Test that authors can update their own posts."""
        post = Post.objects.create(
            title='Original Title',
            content='Original content',
            author=self.user,
            is_published=True
        )
        
        self.client.login(username='testuser', password='testpass123')
        
        # Access edit page
        response = self.client.get(reverse('post_update', kwargs={'pk': post.pk}))
        self.assertEqual(response.status_code, 200)
        
    def test_post_ordering(self):
        """Test that posts are ordered by publication date."""
        # Create posts with different timestamps
        post1 = Post.objects.create(
            title='First Post',
            content='First content',
            author=self.user,
            is_published=True
        )
        
        post2 = Post.objects.create(
            title='Second Post',
            content='Second content',
            author=self.user,
            is_published=True
        )
        
        # Get posts in list order
        posts = list(Post.objects.all())
        
        # Second post should come first (newest first)
        self.assertEqual(posts[0], post2)
        self.assertEqual(posts[1], post1)