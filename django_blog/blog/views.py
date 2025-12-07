from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.contrib import messages
from typing import Union, TYPE_CHECKING, cast
from .forms import CustomUserCreationForm, ProfileForm, PostForm, CommentForm, SearchForm
from .models import Profile, Post, Comment, Tag
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse
from django.db.models import Q, Count

if TYPE_CHECKING:
    from django.contrib.auth.models import User

# Create your views here.
def register(request: HttpRequest) -> Union[HttpResponse, HttpResponseRedirect]:
  """
    Handles both displaying the registration form (GET) 
    and processing the submitted data (POST).
    """
  if request.method == 'POST':
    #1. Bind the POST data to the form
    form = CustomUserCreationForm(request.POST)

    #2. Check for form validity
    if form.is_valid():
      #3. Save the new user and hash the password
      user = form.save()

      #Optional: Log the user in immediately after successful registration
      login(request, user)

      # 4. Redirect to the homepage (or whatever LOGIN_REDIRECT_URL is set to)
      # This implements the Post/Redirect/Get pattern
      return redirect('home')
    
  else:
    # GET Request: Display a blank form
    form = CustomUserCreationForm()

  # Always render the template, passing the form (either blank or with data)
  context = {'form': form}
  return render(request, 'blog/register.html', context)

def home(request: HttpRequest) -> HttpResponse:
    """
    Redirect to the blog posts list (home page).
    """
    return redirect('post_list')

@login_required
def profile_view(request: HttpRequest) -> HttpResponse:
    """
    Display the user's profile page with their account information.
    Requires user to be logged in.
    """
    # Get or create the user's profile
    profile, _ = Profile.objects.get_or_create(user=request.user)
    
    context = {
        'user': request.user,
        'profile': profile,
        'title': 'User Profile'
    }
    return render(request, 'blog/profile.html', context)

@login_required
def profile_edit(request: HttpRequest) -> Union[HttpResponse, HttpResponseRedirect]:
    """
    Handle profile editing for authenticated users.
    GET: Display the profile edit form
    POST: Process the form submission and update user profile
    """
    # Get or create the user's profile
    profile, _ = Profile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProfileForm(instance=profile)
    
    context = {
        'form': form,
        'title': 'Edit Profile'
    }
    return render(request, 'blog/profile_edit.html', context)


# Blog Post CRUD Views
class PostListView(ListView):
    """
    Display a list of all published blog posts.
    Accessible to all users (authenticated and anonymous).
    """
    model = Post
    template_name = 'blog/post_list.html'
    context_object_name = 'posts'
    paginate_by = 10
    
    def get_queryset(self):
        """Return only published posts, ordered by publication date."""
        return Post.objects.filter(is_published=True).select_related('author')


class PostDetailView(DetailView):
    """
    Display a single blog post in detail with its comments.
    Accessible to all users for published posts.
    """
    model = Post
    template_name = 'blog/post_detail.html'
    context_object_name = 'post'
    
    def get_queryset(self):
        """Return only published posts."""
        return Post.objects.filter(is_published=True).select_related('author')
    
    def get_context_data(self, **kwargs):
        """Add comments and comment form to context."""
        context = super().get_context_data(**kwargs)
        post: Post = cast(Post, self.get_object())
        
        # Add comments for this post
        # Using type: ignore to handle Pylance's limitation with Django reverse relations
        context['comments'] = post.comments.select_related('author').all()  # type: ignore
        
        # Add comment form for authenticated users
        if self.request.user.is_authenticated:
            context['comment_form'] = CommentForm()
        
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    """
    Allow authenticated users to create new blog posts.
    Automatically sets the author to the current user.
    """
    model = Post
    form_class = PostForm
    template_name = 'blog/post_form.html'
    success_url = '/posts/'
    
    def form_valid(self, form):
        """Set the author to the current user before saving."""
        form.instance.author = self.request.user
        messages.success(self.request, 'Your blog post has been created successfully!')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        """Add page title to context."""
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create New Post'
        return context


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    Allow post authors to edit their own posts.
    Only the author can edit their posts.
    """
    model = Post
    form_class = PostForm
    template_name = 'blog/post_form.html'
    success_url = '/posts/'
    
    def form_valid(self, form):
        """Save the updated post."""
        messages.success(self.request, 'Your blog post has been updated successfully!')
        return super().form_valid(form)
    
    def test_func(self):
        """Check if the current user is the author of the post."""
        post = cast(Post, self.get_object())
        return post.author == self.request.user
    
    def get_context_data(self, **kwargs):
        """Add page title to context."""
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Post'
        return context


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    Allow post authors to delete their own posts.
    Only the author can delete their posts.
    """
    model = Post
    template_name = 'blog/post_confirm_delete.html'
    success_url = '/posts/'
    
    def test_func(self):
        """Check if the current user is the author of the post."""
        post = cast(Post, self.get_object())
        return post.author == self.request.user
    
    def delete(self, request, *args, **kwargs):
        """Override delete to add success message."""
        messages.success(self.request, 'Your blog post has been deleted successfully!')
        return super().delete(request, *args, **kwargs)


# Search and Tag Views

def search_posts(request: HttpRequest) -> HttpResponse:
    """
    Search for posts based on query string.
    Searches through title, content, and tags.
    """
    query = request.GET.get('q', '').strip()
    posts = Post.objects.none()  # Empty queryset by default
    
    if query:
        # Search across title, content, and tags using Q objects
        posts = Post.objects.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(tags__name__icontains=query),
            is_published=True
        ).distinct().select_related('author').prefetch_related('tags')
    
    form = SearchForm(request.GET)
    
    context = {
        'form': form,
        'posts': posts,
        'query': query,
        'title': f"Search Results for '{query}'" if query else "Search Posts"
    }
    return render(request, 'blog/search_results.html', context)


def posts_by_tag(request: HttpRequest, tag_name: str) -> HttpResponse:
    """
    Display all posts associated with a specific tag.
    """
    tag = get_object_or_404(Tag, name=tag_name)
    posts = Post.objects.filter(tags=tag, is_published=True).select_related('author').prefetch_related('tags')
    
    context = {
        'tag': tag,
        'posts': posts,
        'title': f"Posts tagged with '{tag_name}'"
    }
    return render(request, 'blog/posts_by_tag.html', context)


def all_tags(request: HttpRequest) -> HttpResponse:
    """
    Display all available tags with post counts.
    """
    tags = Tag.objects.annotate(
        post_count=Count('posts', filter=Q(posts__is_published=True))
    ).filter(post_count__gt=0).order_by('name')
    
    context = {
        'tags': tags,
        'title': 'All Tags'
    }
    return render(request, 'blog/all_tags.html', context)


# Comment CRUD Views

class CommentCreateView(LoginRequiredMixin, CreateView):
    """
    Allow authenticated users to create new comments on blog posts.
    Associates the comment with the specified post.
    """
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment_form.html'
    
    def dispatch(self, request, *args, **kwargs):
        """Extract pk from URL kwargs and store it."""
        self.pk = kwargs.get('pk')
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        """Add page title and post context."""
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add Comment'
        
        # Get the parent post for context
        try:
            post = Post.objects.get(id=self.pk, is_published=True)
            context['post'] = post
        except Post.DoesNotExist:
            messages.error(self.request, 'Post not found.')
            # This will be handled by form_valid with a redirect
        return context
    
    def form_valid(self, form):
        """Set the post and author before saving the comment."""
        try:
            post = Post.objects.get(id=self.pk, is_published=True)
            comment = form.save(commit=False)
            comment.post = post
            comment.author = self.request.user
            messages.success(self.request, 'Your comment has been added successfully!')
            return super().form_valid(form)
        except Post.DoesNotExist:
            messages.error(self.request, 'Post not found.')
            return redirect('post_list')
    
    def get_success_url(self):
        """Redirect to the parent post after successful comment creation."""
        return reverse('post_detail', kwargs={'pk': self.pk})


@login_required
def add_comment(request: HttpRequest, post_id: int) -> Union[HttpResponse, HttpResponseRedirect]:
    """
    Add a new comment to a blog post.
    Requires user to be logged in.
    (Legacy function-based view - kept for backwards compatibility)
    """
    if request.method != 'POST':
        return redirect('post_detail', pk=post_id)
    
    try:
        post = Post.objects.get(id=post_id, is_published=True)
    except Post.DoesNotExist:
        messages.error(request, 'Post not found.')
        return redirect('post_list')
    
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.author = request.user
        comment.save()
        messages.success(request, 'Your comment has been added successfully!')
    else:
        messages.error(request, 'Please correct the errors below.')
    
    return redirect('post_detail', pk=post_id)


class CommentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    Allow comment authors to edit their own comments.
    Only the author can edit their comments.
    """
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment_form.html'
    
    def test_func(self):
        """Check if the current user is the author of the comment."""
        comment = cast(Comment, self.get_object())
        return comment.author == self.request.user
    
    def form_valid(self, form):
        """Save the updated comment."""
        messages.success(self.request, 'Your comment has been updated successfully!')
        return super().form_valid(form)
    
    def get_success_url(self):
        """Redirect to the parent post after successful update."""
        comment = cast(Comment, self.get_object())
        return reverse('post_detail', kwargs={'pk': comment.post.id})
    
    def get_context_data(self, **kwargs):
        """Add page title to context."""
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Comment'
        return context


class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    Allow comment authors to delete their own comments.
    Only the author can delete their comments.
    """
    model = Comment
    template_name = 'blog/comment_confirm_delete.html'
    
    def test_func(self):
        """Check if the current user is the author of the comment."""
        comment = cast(Comment, self.get_object())
        return comment.author == self.request.user
    
    def delete(self, request, *args, **kwargs):
        """Override delete to add success message and get post ID."""
        comment = cast(Comment, self.get_object())
        post_id = comment.post.id
        messages.success(request, 'Your comment has been deleted successfully!')
        return super().delete(request, *args, **kwargs)
    
    def get_success_url(self):
        """Redirect to the parent post after successful deletion."""
        comment = cast(Comment, self.get_object())
        return reverse('post_detail', kwargs={'pk': comment.post.id})