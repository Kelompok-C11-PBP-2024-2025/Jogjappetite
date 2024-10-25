from django.shortcuts import redirect
from functools import wraps
from authentication.models import UserProfile

def user_is_owner(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            if user_profile.user_type == 'restaurant':
                return view_func(request, *args, **kwargs)
        except UserProfile.DoesNotExist:
            pass
        return redirect('explore:show_explore_page')
    return _wrapped_view


def user_is_customer(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            if user_profile.user_type == 'customer':
                return view_func(request, *args, **kwargs)
        except UserProfile.DoesNotExist:
            pass
        return redirect('explore:show_explore_page')
    return _wrapped_view