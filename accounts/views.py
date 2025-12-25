from django.shortcuts import redirect
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required


@login_required
def logout_view(request):
    """Logout user and redirect to login page"""
    logout(request)
    return redirect('accounts:login')
