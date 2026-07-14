from django.shortcuts import redirect
from django.contrib import messages

def role_required(role):
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if role == 'kecamatan':
                if not hasattr(request.user, 'admin_kecamatan'):
                    messages.error(request, 'Anda tidak punya akses')
                    return redirect('login')

            elif role == 'desa':
                if not hasattr(request.user, 'desa'):
                    messages.error(request, 'Anda tidak punya akses')
                    return redirect('login')

            else:
                messages.error(request, 'Role tidak dikenali')
                return redirect('login')

            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator