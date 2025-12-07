from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.contrib import messages
from typing import Union, TYPE_CHECKING, cast
from .forms import CustomUserCreationForm, ProfileForm, PostForm
from .models import Profile, Post
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

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
    Display a single blog post in detail.
    Accessible to all users for published posts.
    """
    model = Post
    template_name = 'blog/post_detail.html'
    context_object_name = 'post'
    
    def get_queryset(self):
        """Return only published posts."""
        return Post.objects.filter(is_published=True).select_related('author')


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