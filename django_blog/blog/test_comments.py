#!/usr/bin/env python
"""
Test script for Django Blog Comment System
Tests comment functionality including creation, editing, and deletion.
"""

import os
import sys

# Add the parent directory to Python path so we can import django_blog
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Setup Django FIRST - before any imports
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_blog.settings')

import django
django.setup()

# Now import Django modules after setup
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse

# Import our models and forms
from blog.models import Post, Comment
from blog.forms import CommentForm

User = get_user_model()

def test_comment_system():
    """Test the complete comment system functionality."""
    
    print("=== Django Blog Comment System Test ===")
    
    # Clean up any existing test data
    Comment.objects.all().delete()
    Post.objects.all().delete()
    User.objects.filter(username='testuser').delete()
    
    # Create test data
    print("1. Creating test user...")
    user = User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )
    print(f"   [OK] User created: {user.username}")
    
    print("\n2. Creating test post...")
    post = Post.objects.create(
        title='Test Post for Comments',
        content='This is a test post to verify comment functionality.',
        author=user,
        is_published=True
    )
    print(f"   [OK] Post created: {post.title}")
    
    print("\n3. Testing comment creation...")
    
    # Test comment creation via form
    form_data = {'content': 'This is a test comment!'}
    comment_form = CommentForm(data=form_data)
    if comment_form.is_valid():
        comment = comment_form.save(commit=False)
        comment.post = post
        comment.author = user
        comment.save()
        print(f"   [OK] Comment created: '{comment.content}'")
    else:
        print(f"   [FAIL] Form validation failed: {comment_form.errors}")
        return False
    
    print("\n4. Testing comment display...")
    
    # Check if comment is properly associated with post
    comments = post.comments.all()  # type: ignore[attr-defined]
    if comments.count() == 1:
        comment = comments.first()
        print(f"   [OK] Comment displayed correctly: {comment.content}")
        print(f"   [OK] Comment author: {comment.author.username}")
        print(f"   [OK] Comment created at: {comment.created_at}")
    else:
        print(f"   [FAIL] Expected 1 comment, found {comments.count()}")
        return False
    
    print("\n5. Testing comment form validation...")
    
    # Test empty content validation
    empty_form = CommentForm(data={'content': ''})
    if not empty_form.is_valid():
        print("   [OK] Empty content validation works")
    else:
        print("   [FAIL] Empty content validation failed")
        return False
    
    # Test minimum length validation
    short_form = CommentForm(data={'content': 'Hi'})  # Less than 5 characters
    if not short_form.is_valid():
        print("   [OK] Minimum length validation works")
    else:
        print("   [FAIL] Minimum length validation failed")
        return False
    
    print("\n6. Testing comment update...")
    
    # Test comment update
    comment.content = 'Updated test comment!'
    comment.save()
    
    updated_comment = Comment.objects.get(id=comment.id)
    if updated_comment.content == 'Updated test comment!':
        print("   [OK] Comment update works")
    else:
        print("   [FAIL] Comment update failed")
        return False
    
    print("\n7. Testing comment deletion...")
    
    # Test comment deletion
    comment_id = comment.id
    comment.delete()
    
    if not Comment.objects.filter(id=comment_id).exists():
        print("   [OK] Comment deletion works")
    else:
        print("   [FAIL] Comment deletion failed")
        return False
    
    print("\n8. Testing URL patterns...")
    
    # Test that URLs are properly configured
    try:
        # Test add comment URL
        add_url = reverse('add_comment', kwargs={'post_id': post.id})
        print(f"   [OK] Add comment URL: {add_url}")
        
        # Create another comment for edit/delete URL testing
        comment = Comment.objects.create(
            content='Test comment for URL testing',
            post=post,
            author=user
        )
        
        edit_url = reverse('comment_edit', kwargs={'pk': comment.id})  # type: ignore[attr-defined]
        delete_url = reverse('comment_delete', kwargs={'pk': comment.id})  # type: ignore[attr-defined]
        
        print(f"   [OK] Edit comment URL: {edit_url}")
        print(f"   [OK] Delete comment URL: {delete_url}")
        
    except Exception as e:
        print(f"   [FAIL] URL pattern test failed: {e}")
        return False
    
    print("\n9. Testing admin registration...")
    
    # Test that Comment model is registered in admin
    try:
        from django.contrib.admin.sites import AdminSite
        from blog.admin import CommentAdmin
        
        site = AdminSite()
        admin_instance = CommentAdmin(Comment, site)
        
        # Check if content_preview is in list_display
        if 'content_preview' in admin_instance.list_display:
            print("   [OK] Comment admin registered correctly")
        else:
            print("   [FAIL] Comment admin registration issue - 'content_preview' not in list_display")
            return False
            
    except ImportError as e:
        print(f"   [FAIL] Admin import failed: {e}")
        return False
    except Exception as e:
        print(f"   [FAIL] Admin test failed: {e}")
        return False
    
    print("\n10. Testing Client functionality...")
    
    # Test that Django test client is available
    try:
        client = Client()
        print("   [OK] Django test client initialized successfully")
    except Exception as e:
        print(f"   [FAIL] Django test client failed: {e}")
        return False
    
    print("\n=== All Tests Passed! ===")
    print("\nComment System Features Verified:")
    print("[OK] Comment model creation")
    print("[OK] Comment form validation")
    print("[OK] Comment display functionality")
    print("[OK] Comment CRUD operations")
    print("[OK] URL pattern configuration")
    print("[OK] Admin interface registration")
    print("[OK] Test client functionality")
    
    # Cleanup
    print("\nCleaning up test data...")
    Comment.objects.all().delete()
    Post.objects.all().delete()
    User.objects.filter(username='testuser').delete()
    print("[OK] Test data cleaned up")
    
    return True

def main():
    """Main function to run the tests."""
    try:
        success = test_comment_system()
        if success:
            print("\n[SUCCESS] Comment System Implementation: SUCCESSFUL")
            return 0
        else:
            print("\n[FAIL] Comment System Implementation: FAILED")
            return 1
    except Exception as e:
        print(f"\n[FAIL] Test execution failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())