from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required


def redirect_by_role(request):
    user = request.user

    if hasattr(user, 'admin_kecamatan'):      
        return redirect('kecamatan_dashboard')
    elif hasattr(user, 'desa'):               
        return redirect('desa_dashboard')
    logout(request)
    messages.error(request, 'Akun ini tidak memiliki role yang valid.')
    return redirect('login')

def login_view(request):
    if request.user.is_authenticated:
        return redirect_by_role(request)

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect_by_role(request)
        else:
            messages.error(request, 'Username atau password salah')

    return render(request, 'auth/login.html')


@login_required
def logout_view(request):
    logout(request)
    return redirect('login')