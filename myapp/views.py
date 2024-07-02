from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Profile
from django.core.exceptions import ValidationError
from django.db import IntegrityError


def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')

        # Validate input fields
        if not username or not email or not password or not password_confirm:
            messages.warning(request, 'All fields are required.')
        elif password != password_confirm:
            messages.warning(request, 'Passwords do not match.')
        elif User.objects.filter(username=username).exists():
            messages.warning(request, 'Username is already taken.')
        elif User.objects.filter(email=email).exists():
            messages.warning(request, 'Email is already registered.')
        else:
            try:
                # Create the user
                user = User.objects.create_user(username=username, email=email, password=password)
                Profile.objects.create(user=user)

                # Authenticate and log in the user
                user = authenticate(username=username, password=password)
                if user is not None:
                    login(request, user)
                    messages.success(request, 'Registration successful! Welcome, {}!'.format(username))
                    return redirect('profile')  # Redirect to the profile page
                else:
                    messages.error(request, 'Authentication failed. Please try logging in.')

            except ValidationError as e:
                messages.error(request, f'Validation error: {e}')
            except Exception as e:
                messages.error(request, f'An error occurred: {e}')

    return render(request, 'register.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Welcome back, {}!'.format(username))
            return redirect('profile')  # Redirect to profile page on successful login
        else:
            messages.error(request, 'Invalid username or password. Please try again.')

    return render(request, 'login.html')

@login_required
def profile_view(request):
    try:
        profile = Profile.objects.get(user=request.user)
        return render(request, 'profile.html', {'profile': profile})
    except Profile.DoesNotExist:
        messages.error(request, 'Profile does not exist. Please complete your profile.')
        return redirect('profile_edit')  # Redirect to a profile creation or edit page

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')  # Redirect to login page after logout
