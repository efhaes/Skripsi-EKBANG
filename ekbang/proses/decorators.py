from django.shortcuts import redirect
from django.contrib import messages

def role_required(role):
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if not hasattr(request.user, 'profile'):
                messages.error(request, 'Role tidak ditemukan')
                return redirect('login')

            if request.user.profile.role != role:
                messages.error(request, 'Anda tidak punya akses')
                return redirect('login')

            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
