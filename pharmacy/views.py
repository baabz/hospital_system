from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import F, Q
from .models import Medication, MedicationDispensing, StockAdjustment


@login_required
def medication_list(request):
    """List all medications with search and filter"""
    medications = Medication.objects.all().order_by('name')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    category_filter = request.GET.get('category', '')
    stock_filter = request.GET.get('stock', '')
    
    if search_query:
        medications = medications.filter(
            Q(name__icontains=search_query) | 
            Q(generic_name__icontains=search_query) |
            Q(manufacturer__icontains=search_query)
        )
    
    if category_filter:
        medications = medications.filter(category=category_filter)
    
    if stock_filter == 'low':
        medications = medications.filter(quantity_in_stock__lte=F('reorder_level'))
    elif stock_filter == 'out':
        medications = medications.filter(quantity_in_stock=0)
    
    # Check for low stock
    low_stock = Medication.objects.filter(quantity_in_stock__lte=F('reorder_level'))
    
    context = {
        'medications': medications,
        'low_stock_count': low_stock.count(),
        'search_query': search_query,
        'category_filter': category_filter,
        'stock_filter': stock_filter,
        'categories': Medication.CATEGORY_CHOICES,
    }
    return render(request, 'pharmacy/medication_list.html', context)


@login_required
def dispensing_list(request):
    """List medication dispensing records"""
    dispensing_records = MedicationDispensing.objects.select_related(
        'medication', 'prescription', 'dispensed_by'
    ).order_by('-dispensed_at')
    
    context = {'dispensing_records': dispensing_records}
    return render(request, 'pharmacy/dispensing_list.html', context)
