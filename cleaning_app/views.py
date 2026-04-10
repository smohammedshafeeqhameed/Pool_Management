from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from .models import Villa, CleaningRecord, PaymentRecord
from .forms import VillaForm, CleaningRecordForm, PaymentRecordForm

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def dashboard(request):
    villas = Villa.objects.all().order_by('-created_at')
    return render(request, 'cleaning_app/dashboard.html', {'villas': villas})

@login_required
def add_villa(request):
    if request.method == 'POST':
        form = VillaForm(request.POST)
        if form.is_valid():
            villa = form.save(commit=False)
            villa.added_by = request.user
            villa.save()
            return redirect('dashboard')
    else:
        form = VillaForm()
    return render(request, 'cleaning_app/add_villa.html', {'form': form})

@login_required
def villa_detail(request, villa_id):
    villa = get_object_or_404(Villa, pk=villa_id)
    records = villa.cleaning_records.all().order_by('-date')
    payments = villa.payment_records.all().order_by('-month_year')[:6]  # Show last 6 months
    return render(request, 'cleaning_app/villa_detail.html', {
        'villa': villa, 
        'records': records,
        'payments': payments
    })

@login_required
def manage_payments(request, villa_id):
    villa = get_object_or_404(Villa, pk=villa_id)
    payments = villa.payment_records.all()
    
    if request.method == 'POST':
        form = PaymentRecordForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.villa = villa
            payment.save()
            return redirect('manage_payments', villa_id=villa.id)
    else:
        form = PaymentRecordForm()
        
    return render(request, 'cleaning_app/manage_payments.html', {
        'villa': villa,
        'payments': payments,
        'form': form
    })

@login_required
def update_payment(request, payment_id):
    payment = get_object_or_404(PaymentRecord, pk=payment_id)
    if request.method == 'POST':
        # Simple toggle or update logic
        action = request.POST.get('action')
        if action == 'toggle_bill':
            payment.bill_given = not payment.bill_given
        elif action == 'toggle_paid':
            payment.is_paid = not payment.is_paid
        elif action == 'update_amount':
            try:
                payment.amount_paid = request.POST.get('amount', 0)
            except:
                pass
        payment.save()
    return redirect('manage_payments', villa_id=payment.villa.id)

@login_required
def add_cleaning_record(request, villa_id):
    villa = get_object_or_404(Villa, pk=villa_id)
    if request.method == 'POST':
        form = CleaningRecordForm(request.POST)
        if form.is_valid():
            record = form.save(commit=False)
            record.villa = villa
            record.cleaner = request.user
            record.save()
            return redirect('villa_detail', villa_id=villa.id)
    else:
        form = CleaningRecordForm()
    return render(request, 'cleaning_app/add_cleaning_record.html', {'form': form, 'villa': villa})
