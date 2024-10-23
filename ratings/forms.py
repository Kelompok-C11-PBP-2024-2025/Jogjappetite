from django import forms
from .models import Ratings

class RatingForm(forms.ModelForm):
    class Meta:
        model = Ratings
        fields = ['rating', 'pesan_rating']  # Include fields for rating and review
