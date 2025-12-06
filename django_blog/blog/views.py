from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegistrationForm, UserProfileEditForm
from django.contrib.auth.models import User
from .models import Post
from django.views.generic import ListView

class PostListView(ListView):
  """
    A Class-Based View to list all published blog posts.
    """
  model = Post
  context_object_name = 'posts'
  paginate_by = 10
  template_name = 'blog/post/list.html'

  # Optional: Use queryset to fetch only published posts (professional standard)
    # Since we haven't created the QuerySet Manager yet, we'll order them simply for now
  ordering = ['-publish']

# -- Custom Registration View --
def register_user(request):
  if request.method == 'POST':
    form = UserRegistrationForm(request.POST)
    if form.is_valid():
      user = form.save()
      # Log the user in immediately after registration
      login(request, user)
      messages.success(request, f'Welcom, {user.username}! Your account has been created.')
      # Use 'reverse_lazy' or hardcoded URL; 'post_list' is an assumed name
      return redirect('blog:post_list')
  else:
    form = UserRegistrationForm()

  return render(request, 'registration/register.html', {'form': form})

# --- Profile Management View (Step 4) ---
@login_required
def profile_management(request):
  if request.method == 'POST':
    # Pass the request.user instance to the form for modification
    form = UserProfileEditForm(request.POST, instance=request.user)

    if form.is_valid():
      form.save()
      messages.success(request, 'Your profile was successfully updated!')
      return redirect('blog:profile')
  else:
    form = UserProfileEditForm(isinstance=request.user)

  context = {
    'form': form,
    'title': f'{request.user.username} Profile'
  }

  return render(request, 'registration/profile.html', context)