from django.contrib.auth.forms import UserCreationForm
from django import forms
from authentication.models import UserProfile
from django.contrib.auth.models import User

class SignUpForm(UserCreationForm):
    USER_TYPE_CHOICES = [
        ('customer', 'Customer'),  # lowercase in the database
        ('restaurant', 'Restaurant Owner'),  # lowercase in the database
    ]
    
    user_type = forms.ChoiceField(
        choices=USER_TYPE_CHOICES,  
        label="Choose your user type:",
        required=True
    )
    
    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')
    full_name = forms.CharField(max_length=100, required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'full_name', 'user_type')

    def save(self, commit=True):
        # Save the User model
        user = super(SignUpForm, self).save(commit=False)
        user.email = self.cleaned_data['email']  # Save email to the user model
        
        if commit:
            user.save()

        # Create the UserProfile and link it to the user
        UserProfile.objects.create(
            user=user, 
            user_type=self.cleaned_data['user_type'],  # ensure it's 'customer' or 'restaurant'
            full_name=self.cleaned_data['full_name']
        )
        
        return user
