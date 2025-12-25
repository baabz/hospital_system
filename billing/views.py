from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import timedelta
from django.utils import timezone
from .models import Invoice, InvoiceItem, Payment
from .forms import InvoiceForm, InvoiceItemForm, PaymentForm


@login_required
def invoice_list(request):
    """List all invoices"""
    status_filter = request.GET.get('status', '')
    
    invoices = Invoice.objects.select_related('patient').all()
    
    if status_filter:
        invoices = invoices.filter(status=status_filter)
    
    invoices = invoices.order_by('-created_at')
    
    context = {
        'invoices': invoices,
        'status_filter': status_filter,
    }
    return render(request, 'billing/invoice_list.html', context)


@login_required
def invoice_create(request):
    """Create new invoice"""
    if request.method == 'POST':
        form = InvoiceForm(request.POST)
        if form.is_valid():
            invoice = form.save(commit=False)
            invoice.created_by = request.user
            invoice.status = 'draft'
            invoice.save()
            messages.success(request, f'Invoice {invoice.invoice_number} created! Add line items below.')
            return redirect('billing:invoice_detail', invoice_number=invoice.invoice_number)
    else:
        # Set default due date to 30 days from now
        initial = {'due_date': (timezone.now() + timedelta(days=30)).date()}
        form = InvoiceForm(initial=initial)
    
    context = {'form': form}
    return render(request, 'billing/invoice_form.html', context)


@login_required
def invoice_detail(request, invoice_number):
    """View invoice details"""
    invoice = get_object_or_404(Invoice, invoice_number=invoice_number)
    items = invoice.items.all()
    payments = invoice.payments.all()
    
    context = {
        'invoice': invoice,
        'items': items,
        'payments': payments,
    }
    return render(request, 'billing/invoice_detail.html', context)


@login_required
def invoice_add_item(request, invoice_number):
    """Add item to invoice"""
    invoice = get_object_or_404(Invoice, invoice_number=invoice_number)
    
    if request.method == 'POST':
        form = InvoiceItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.invoice = invoice
            item.save()
            invoice.calculate_total()
            messages.success(request, 'Item added to invoice!')
            return redirect('billing:invoice_detail', invoice_number=invoice.invoice_number)
    else:
        form = InvoiceItemForm()
    
    context = {
        'form': form,
        'invoice': invoice,
    }
    return render(request, 'billing/invoice_item_form.html', context)


@login_required
def invoice_record_payment(request, invoice_number):
    """Record payment for invoice"""
    invoice = get_object_or_404(Invoice, invoice_number=invoice_number)
    
    if request.method == 'POST':
        form = PaymentForm(request.POST, invoice=invoice)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.invoice = invoice
            payment.received_by = request.user
            payment.save()
            messages.success(request, f'Payment of ₦{payment.amount} recorded successfully!')
            return redirect('billing:invoice_detail', invoice_number=invoice.invoice_number)
    else:
        # Default amount to balance due
        initial = {'amount': invoice.balance_due()}
        form = PaymentForm(initial=initial, invoice=invoice)
    
    context = {
        'form': form,
        'invoice': invoice,
    }
    return render(request, 'billing/payment_form.html', context)


# Expense Management Views
from .expenses_models import Expense, ExpenseCategory
from .expenses_forms import ExpenseForm, ExpenseCategoryForm
from django.db.models import Sum
from datetime import datetime, timedelta


@login_required
def expense_list(request):
    """List all expenses"""
    expenses = Expense.objects.select_related('category', 'recorded_by').all()
    
    # Calculate totals
    total_expenses = expenses.aggregate(total=Sum('amount'))['total'] or 0
    
    context = {
        'expenses': expenses,
        'total_expenses': total_expenses,
    }
    return render(request, 'billing/expense_list.html', context)


@login_required
def expense_create(request):
    """Record new expense"""
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.recorded_by = request.user
            expense.save()
            messages.success(request, f'Expense of ₦{expense.amount} recorded successfully!')
            return redirect('billing:expense_list')
    else:
        form = ExpenseForm()
    
    context = {'form': form}
    return render(request, 'billing/expense_form.html', context)


@login_required
def financial_report(request):
    """Financial report with income vs expenses"""
    # Get date range (default: current month)
    today = timezone.now().date()
    start_date = request.GET.get('start_date', today.replace(day=1))
    end_date = request.GET.get('end_date', today)
    
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    # Calculate income (from payments)
    income = Payment.objects.filter(
        payment_date__gte=start_date,
        payment_date__lte=end_date
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Calculate expenses
    expenses = Expense.objects.filter(
        expense_date__gte=start_date,
        expense_date__lte=end_date
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Calculate profit
    profit = income - expenses
    
    # Expense breakdown by type
    expense_breakdown = Expense.objects.filter(
        expense_date__gte=start_date,
        expense_date__lte=end_date
    ).values('expense_type').annotate(total=Sum('amount')).order_by('-total')
    
    context = {
        'start_date': start_date,
        'end_date': end_date,
        'income': income,
        'expenses': expenses,
        'profit': profit,
        'expense_breakdown': expense_breakdown,
    }
    return render(request, 'billing/financial_report.html', context)

