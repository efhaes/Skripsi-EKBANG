from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required

def login_view(request):
    if request.user.is_authenticated:
        return redirect_by_role(request.user)

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect_by_role(user)
        else:
            messages.error(request, 'Username atau password salah')

    return render(request, 'auth/login.html')


@login_required
def logout_view(request):
    logout(request)
    return redirect('login')


def redirect_by_role(user):
    if hasattr(user, 'profile'):
        if user.profile.role == 'desa':
            return redirect('desa_dashboard')
        elif user.profile.role == 'kecamatan':
            return redirect('kecamatan_dashboard')

    messages.error(user, 'Role tidak dikenali')
    return redirect('login')
