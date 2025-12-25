from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def reports_dashboard(request):
    """Reports dashboard"""
    context = {}
    return render(request, 'reports/dashboard.html', context)
