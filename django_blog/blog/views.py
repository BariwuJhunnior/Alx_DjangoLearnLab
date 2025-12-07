from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.contrib import messages
from typing import Union
from .forms import CustomUserCreationForm, ProfileForm
from .models import Profile
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required

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
    Display the home page of the blog.
    """
    context = {
        'title': 'Home'
    }
    return render(request, 'blog/base.html', context)

@login_required
def profile_view(request: HttpRequest) -> HttpResponse:
    """
    Display the user's profile page with their account information.
    Requires user to be logged in.
    """
    # Get or create the user's profile
    profile, created = Profile.objects.get_or_create(user=request.user)
    
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
    profile, created = Profile.objects.get_or_create(user=request.user)
    
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