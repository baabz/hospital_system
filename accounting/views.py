from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum, Q, Count
from datetime import datetime, timedelta
from .models import PaymentRecord, ExpenseRecord, DailyCashSummary
from .forms import PaymentRecordForm, ExpenseRecordForm, DailyCashSummaryForm, DateRangeFilterForm


@login_required
def accounting_dashboard(request):
    """Main accounting dashboard with today's summary"""
    today = timezone.now().date()
    
    # Get filter parameters
    filter_form = DateRangeFilterForm(request.GET)
    start_date = request.GET.get('start_date', today)
    end_date = request.GET.get('end_date', today)
    
    # Today's payments
    today_payments = PaymentRecord.objects.filter(payment_date__date=today)
    today_expenses = ExpenseRecord.objects.filter(expense_date__date=today, is_approved=True)
    
    # Calculate totals by payment method
    cash_income = today_payments.filter(payment_method='CASH').aggregate(Sum('amount'))['amount__sum'] or 0
    pos_income = today_payments.filter(payment_method='POS').aggregate(Sum('amount'))['amount__sum'] or 0
    bank_income = today_payments.filter(payment_method='BANK_TRANSFER').aggregate(Sum('amount'))['amount__sum'] or 0
    other_income = today_payments.filter(payment_method__in=['MOBILE_MONEY', 'CHEQUE']).aggregate(Sum('amount'))['amount__sum'] or 0
    
    cash_expenses = today_expenses.filter(payment_method='CASH').aggregate(Sum('amount'))['amount__sum'] or 0
    bank_expenses = today_expenses.filter(payment_method='BANK_TRANSFER').aggregate(Sum('amount'))['amount__sum'] or 0
    other_expenses = today_expenses.filter(payment_method__in=['MOBILE_MONEY', 'CHEQUE', 'DEBIT_CARD']).aggregate(Sum('amount'))['amount__sum'] or 0
    
    total_income = cash_income + pos_income + bank_income + other_income
    total_expenses = cash_expenses + bank_expenses + other_expenses
    net_today = total_income - total_expenses
    
    # Monthly summary
    month_start = today.replace(day=1)
    monthly_payments = PaymentRecord.objects.filter(payment_date__date__gte=month_start)
    monthly_expenses = ExpenseRecord.objects.filter(expense_date__date__gte=month_start, is_approved=True)
    
    monthly_income = monthly_payments.aggregate(Sum('amount'))['amount__sum'] or 0
    monthly_expense_total = monthly_expenses.aggregate(Sum('amount'))['amount__sum'] or 0
    monthly_net = monthly_income - monthly_expense_total
    
    # Payment type breakdown
    payment_types = today_payments.values('payment_type').annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('-total')
    
    # Expense category breakdown
    expense_categories = today_expenses.values('category').annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('-total')
    
    # Pending approvals
    pending_expenses = ExpenseRecord.objects.filter(is_approved=False).count()
    
    context = {
        'today': today,
        'cash_income': cash_income,
        'pos_income': pos_income,
        'bank_income': bank_income,
        'other_income': other_income,
        'total_income': total_income,
        'cash_expenses': cash_expenses,
        'bank_expenses': bank_expenses,
        'other_expenses': other_expenses,
        'total_expenses': total_expenses,
        'net_today': net_today,
        'monthly_income': monthly_income,
        'monthly_expenses': monthly_expense_total,
        'monthly_net': monthly_net,
        'recent_payments': today_payments.order_by('-payment_date')[:10],
        'recent_expenses': today_expenses.order_by('-expense_date')[:10],
        'payment_types': payment_types,
        'expense_categories': expense_categories,
        'pending_expenses': pending_expenses,
        'filter_form': filter_form,
    }
    
    return render(request, 'accounting/dashboard.html', context)


@login_required
def payment_list(request):
    """List all payments with filtering"""
    payments = PaymentRecord.objects.all()
    
    # Apply filters
    if request.GET.get('start_date'):
        payments = payments.filter(payment_date__date__gte=request.GET.get('start_date'))
    if request.GET.get('end_date'):
        payments = payments.filter(payment_date__date__lte=request.GET.get('end_date'))
    if request.GET.get('payment_method'):
        payments = payments.filter(payment_method=request.GET.get('payment_method'))
    if request.GET.get('payment_type'):
        payments = payments.filter(payment_type=request.GET.get('payment_type'))
    
    # Search
    search_query = request.GET.get('q', '')
    if search_query:
        payments = payments.filter(
            Q(payment_id__icontains=search_query) |
            Q(patient__first_name__icontains=search_query) |
            Q(patient__last_name__icontains=search_query) |
            Q(reference_number__icontains=search_query)
        )
    
    context = {
        'payments': payments[:100],  # Limit to 100 for performance
        'filter_form': DateRangeFilterForm(request.GET),
        'search_query': search_query,
    }
    
    return render(request, 'accounting/payment_list.html', context)


@login_required
def payment_record(request):
    """Record a new payment"""
    if request.method == 'POST':
        form = PaymentRecordForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.received_by = request.user
            payment.save()
            
            messages.success(request, f'Payment {payment.payment_id} recorded successfully!')
            return redirect('accounting:dashboard')
    else:
        form = PaymentRecordForm()
        
        # Pre-fill patient if provided in URL
        patient_id = request.GET.get('patient')
        if patient_id:
            form.initial['patient'] = patient_id
        
        # Pre-fill invoice if provided in URL
        invoice_id = request.GET.get('invoice')
        if invoice_id:
            form.initial['invoice'] = invoice_id
            form.initial['payment_type'] = 'INVOICE'
    
    context = {
        'form': form,
        'title': 'Record Payment',
    }
    
    return render(request, 'accounting/payment_form.html', context)


@login_required
def expense_list(request):
    """List all expenses with filtering"""
    expenses = ExpenseRecord.objects.all()
    
    # Apply filters
    if request.GET.get('start_date'):
        expenses = expenses.filter(expense_date__date__gte=request.GET.get('start_date'))
    if request.GET.get('end_date'):
        expenses = expenses.filter(expense_date__date__lte=request.GET.get('end_date'))
    if request.GET.get('category'):
        expenses = expenses.filter(category=request.GET.get('category'))
    if request.GET.get('is_approved'):
        expenses = expenses.filter(is_approved=request.GET.get('is_approved') == 'true')
    
    # Search
    search_query = request.GET.get('q', '')
    if search_query:
        expenses = expenses.filter(
            Q(expense_id__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(vendor__icontains=search_query)
        )
    
    context = {
        'expenses': expenses[:100],
        'search_query': search_query,
    }
    
    return render(request, 'accounting/expense_list.html', context)


@login_required
def expense_record(request):
    """Record a new expense"""
    if request.method == 'POST':
        form = ExpenseRecordForm(request.POST, request.FILES)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.recorded_by = request.user
            expense.save()
            
            messages.success(request, f'Expense {expense.expense_id} recorded successfully!')
            return redirect('accounting:expense_list')
    else:
        form = ExpenseRecordForm()
    
    context = {
        'form': form,
        'title': 'Record Expense',
    }
    
    return render(request, 'accounting/expense_form.html', context)


@login_required
def expense_approve(request, pk):
    """Approve an expense"""
    expense = get_object_or_404(ExpenseRecord, pk=pk)
    
    if not expense.is_approved:
        expense.approve(request.user)
        messages.success(request, f'Expense {expense.expense_id} approved successfully!')
    else:
        messages.info(request, f'Expense {expense.expense_id} is already approved.')
    
    return redirect('accounting:expense_list')


@login_required
def daily_report(request):
    """Generate daily financial report"""
    date_str = request.GET.get('date', timezone.now().date().isoformat())
    report_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    
    payments = PaymentRecord.objects.filter(payment_date__date=report_date)
    expenses = ExpenseRecord.objects.filter(expense_date__date=report_date, is_approved=True)
    
    # Get or create daily summary
    summary, created = DailyCashSummary.objects.get_or_create(date=report_date)
    if created or not summary.is_reconciled:
        summary.calculate_totals()
    
    context = {
        'report_date': report_date,
        'summary': summary,
        'payments': payments,
        'expenses': expenses,
    }
    
    return render(request, 'accounting/daily_report.html', context)


@login_required
def cash_reconciliation(request):
    """Daily cash reconciliation"""
    today = timezone.now().date()
    
    # Get or create today's summary
    summary, created = DailyCashSummary.objects.get_or_create(date=today)
    
    if request.method == 'POST':
        form = DailyCashSummaryForm(request.POST, instance=summary)
        if form.is_valid():
            summary = form.save(commit=False)
            summary.calculate_totals()
            summary.is_reconciled = True
            summary.reconciled_by = request.user
            summary.reconciled_at = timezone.now()
            summary.save()
            
            messages.success(request, f'Cash reconciliation for {today} completed successfully!')
            return redirect('accounting:dashboard')
    else:
        # Auto-calculate totals
        summary.calculate_totals()
        form = DailyCashSummaryForm(instance=summary)
    
    context = {
        'form': form,
        'summary': summary,
        'today': today,
    }
    
    return render(request, 'accounting/reconciliation.html', context)
