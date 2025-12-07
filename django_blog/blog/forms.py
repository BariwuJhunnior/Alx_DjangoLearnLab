from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth import get_user_model
from django import forms
from .models import Profile

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
  """
    A custom form for creating new users that extends the standard
    UserCreationForm to explicitly include the email field.
    """
  class Meta:
    #Inherit the model from the parent form
    model = User

    # Define all the fields to be included.
    # 'username' and the two password fields are included implicitly
    # by the parent, but we list them explicitly along with 'email'.
    # We also want the email field to be visible during registration.

    fields = ('username', 'email')

class ProfileForm(forms.ModelForm):
    """
    Form for editing user profile information.
    This form handles both User model fields and Profile model fields.
    """
    email = forms.EmailField(required=True, help_text="A valid email address is required")
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)
    
    class Meta:
        model = Profile
        fields = ('bio', 'profile_picture', 'website', 'location', 'birth_date')
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Tell us about yourself...'}),
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'website': forms.URLInput(attrs={'placeholder': 'https://example.com'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate User fields from the instance
        if self.instance and self.instance.user:
            self.fields['email'].initial = self.instance.user.email
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
    
    def save(self, commit=True):
        profile = super().save(commit=False)
        
        # Update User model fields
        if self.instance and self.instance.user:
            user = self.instance.user
            user.email = self.cleaned_data['email']
            user.first_name = self.cleaned_data['first_name']
            user.last_name = self.cleaned_data['last_name']
            if commit:
                user.save()
        
        if commit:
            profile.save()
        return profile
    