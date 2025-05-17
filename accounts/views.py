# accounts/views.py

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm, LoginForm

def register_view(request):
    if request.user.is_authenticated:
        return redirect('store:home')
        
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "¡Registro exitoso! Bienvenido.")
            return redirect('store:home')
    else:
        form = RegisterForm()
    
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('store:home')
        
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Bienvenido de nuevo, {user.username}!")
                next_url = request.GET.get('next', 'store:home')
                return redirect(next_url)
        else:
            messages.error(request, "Usuario o contraseña incorrectos.")
    else:
        form = LoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "Sesión cerrada exitosamente.")
    return redirect('store:home')

@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html')