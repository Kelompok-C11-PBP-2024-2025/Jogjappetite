from django.contrib.auth.forms import UserCreationForm
from django import forms
from authentication.models import UserProfile
from django.contrib.auth.models import User

class SignUpForm(UserCreationForm):
    USER_TYPE_CHOICES = [
        ('customer', 'Customer'),  
        ('restaurant', 'Restaurant Owner'),  
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
        user = super(SignUpForm, self).save(commit=False)
        user.email = self.cleaned_data['email']  
        
        if commit:
            user.save()

        UserProfile.objects.create(
            user=user, 
            user_type=self.cleaned_data['user_type'], 
            full_name=self.cleaned_data['full_name']
        )
        
        return user
