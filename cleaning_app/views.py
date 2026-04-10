from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from .models import Villa, CleaningRecord, PaymentRecord
from .forms import VillaForm, CleaningRecordForm, PaymentRecordForm
import datetime

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
    today = datetime.date.today()
    current_month = today.replace(day=1)
    
    # Only show current month based on user request
    months_to_show = [current_month]
    
    payment_filter = request.GET.get('payment_filter')
    if payment_filter is None:
        payment_filter = 'default_split'
    
    villas_query = Villa.objects.all().order_by('-created_at')
    
    # Define variables to avoid UnboundLocalError
    villas = []
    villas_bg_unpaid = []
    villas_bng_unpaid = []
    
    # Process Filter based on current month
    from django.db.models import Q
    
    if payment_filter == 'default_split':
        # Split into two lists
        q_bg_unpaid = villas_query.filter(
            payment_records__month_year=current_month, 
            payment_records__is_paid=False, 
            payment_records__bill_given=True
        )
        q_bng_unpaid = villas_query.exclude(
            payment_records__month_year=current_month, payment_records__bill_given=True
        ).exclude(
            payment_records__month_year=current_month, payment_records__is_paid=True
        )
        
        villas_bg_unpaid = list(q_bg_unpaid.prefetch_related('payment_records'))
        villas_bng_unpaid = list(q_bng_unpaid.prefetch_related('payment_records'))
        
        # Attach recent payments to split lists
        for v_list in [villas_bg_unpaid, villas_bng_unpaid]:
            for villa in v_list:
                villa.recent_payments = []
                payment_dict = {p.month_year: p for p in villa.payment_records.all()}
                for m in reversed(months_to_show):
                    villa.recent_payments.append({'month': m, 'record': payment_dict.get(m, None)})
    elif payment_filter:
        if payment_filter == 'bg_paid':
            villas_query = villas_query.filter(
                payment_records__month_year=current_month, 
                payment_records__is_paid=True, 
                payment_records__bill_given=True
            )
        elif payment_filter == 'bg_unpaid':
            villas_query = villas_query.filter(
                payment_records__month_year=current_month, 
                payment_records__is_paid=False, 
                payment_records__bill_given=True
            )
        elif payment_filter == 'bng_unpaid':
            # Bill not given amount not paid: Either no record, or record with bill_given=False and is_paid=False
            villas_query = villas_query.exclude(
                payment_records__month_year=current_month, payment_records__bill_given=True
            ).exclude(
                payment_records__month_year=current_month, payment_records__is_paid=True
            )
        
        villas = list(villas_query.prefetch_related('payment_records'))
        
        # Attach recent payments
        for villa in villas:
            villa.recent_payments = []
            payment_dict = {p.month_year: p for p in villa.payment_records.all()}
            for m in reversed(months_to_show):
                villa.recent_payments.append({'month': m, 'record': payment_dict.get(m, None)})
    else:
        # e.g., 'all' or empty string
        villas = list(villas_query.prefetch_related('payment_records'))
        for villa in villas:
            villa.recent_payments = []
            payment_dict = {p.month_year: p for p in villa.payment_records.all()}
            for m in reversed(months_to_show):
                villa.recent_payments.append({'month': m, 'record': payment_dict.get(m, None)})

    return render(request, 'cleaning_app/dashboard.html', {
        'villas': villas,
        'villas_bg_unpaid': villas_bg_unpaid,
        'villas_bng_unpaid': villas_bng_unpaid,
        'months': list(reversed(months_to_show)),  # pass the header months
        'current_month': current_month,
        'payment_filter': payment_filter
    })

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
    payments = villa.payment_records.all().order_by('-month_year')[:6]  # Show last 6 months
    return render(request, 'cleaning_app/villa_detail.html', {
        'villa': villa, 
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
def toggle_dashboard_payment(request, villa_id):
    if request.method == 'POST':
        villa = get_object_or_404(Villa, pk=villa_id)
        action = request.POST.get('action')
        month_str = request.POST.get('month_year')
        try:
            year, month, day = map(int, month_str.split('-'))
            month_date = datetime.date(year, month, day)
        except:
            return redirect('dashboard')
            
        payment, created = PaymentRecord.objects.get_or_create(
            villa=villa,
            month_year=month_date
        )
        
        if action == 'toggle_bill':
            payment.bill_given = not payment.bill_given
        elif action == 'toggle_paid':
            payment.is_paid = not payment.is_paid
        
        payment.save()
        
    return redirect('dashboard')


