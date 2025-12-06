from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth import get_user_model

User = get_user_model()

class UserRegistrationForm(UserCreationForm):
  """
    Extends the default UserCreationForm to include the 'email' field.
    """
  
  email = forms.EmailField(required=True, label="Email Address")

  class Meta(UserCreationForm.Meta):
    model = User
    fields = ('username', 'email') + UserCreationForm.Meta.fields[2:]   # Include username and email

    def clean_email(self):
      """
        Ensures the email address is unique across all users.
        """
      email = self.clearned_data.get('email').lower()
      if User.objects.filter(email=email).exists():
        raise forms.ValidationError("A user with this email address already exists.")
      
      return email
    
    def save(self, commit=True):
      """
        Custom save method to set the email field correctly and ensure it is lowercase.
        """
      user = super().save(commit=False)
      user.email = self.cleaned_data['email']
      if commit:
        user.save()
      return user
    
class UserProfileEditForm(UserChangeForm):
  """
    Custom form for authenticated users to edit their profile details.
    Note: We exclude the password field for security (it's handled by a separate view).
    """
  email = forms.EmailField(required=True, label="Email Address")

  class Meta:
    model = User
    fields = ('username', 'email', 'first_name', 'last_name') #fields the user can edit

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    if 'password' in self.fields:
      self.fields.pop('password')
