from django import forms
from .models import Ratings, Menu

class AddRatingForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        restaurant = kwargs.pop('restaurant', None)
        super(AddRatingForm, self).__init__(*args, **kwargs)
        if restaurant:
            self.fields['menu_review'].queryset = Menu.objects.filter(restoran=restaurant)

    class Meta:
        model = Ratings
        fields = ['menu_review', 'rating', 'pesan_rating']
