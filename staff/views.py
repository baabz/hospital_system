from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Department, StaffSchedule, Ward, Bed
from .forms import DepartmentForm
from accounts.models import User


@login_required
def staff_list(request):
    """List all staff members"""
    staff = User.objects.filter(is_active_staff=True).select_related('department').order_by('role', 'last_name')
    
    context = {'staff': staff}
    return render(request, 'staff/staff_list.html', context)


@login_required
def department_list(request):
    """List all departments"""
    departments = Department.objects.prefetch_related('wards').all().order_by('name')
    
    # Count staff per department
    for dept in departments:
        dept.staff_count = User.objects.filter(department=dept).count()
    
    context = {'departments': departments}
    return render(request, 'staff/department_list.html', context)


@login_required
def department_create(request):
    """Create new department"""
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            department = form.save()
            messages.success(request, f'Department "{department.name}" created successfully!')
            return redirect('staff:department_list')
    else:
        form = DepartmentForm()
    
    context = {
        'form': form,
        'title': 'Add New Department',
    }
    return render(request, 'staff/department_form.html', context)


@login_required
def department_edit(request, pk):
    """Edit existing department"""
    department = get_object_or_404(Department, pk=pk)
    
    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=department)
        if form.is_valid():
            department = form.save()
            messages.success(request, f'Department "{department.name}" updated successfully!')
            return redirect('staff:department_list')
    else:
        form = DepartmentForm(instance=department)
    
    context = {
        'form': form,
        'department': department,
        'title': f'Edit {department.name}',
    }
    return render(request, 'staff/department_form.html', context)


@login_required
def department_delete(request, pk):
    """Delete department"""
    department = get_object_or_404(Department, pk=pk)
    
    # Check if department has staff
    staff_count = User.objects.filter(department=department).count()
    
    if request.method == 'POST':
        department_name = department.name
        department.delete()
        messages.success(request, f'Department "{department_name}" deleted successfully!')
        return redirect('staff:department_list')
    
    context = {
        'department': department,
        'staff_count': staff_count,
    }
    return render(request, 'staff/department_confirm_delete.html', context)
