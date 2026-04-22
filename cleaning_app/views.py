from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from .models import Villa, PaymentRecord
from .forms import VillaForm, PaymentPeriodForm, PaymentRecordForm
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
    selected_y = request.GET.get('selected_year')
    y_val = int(selected_y) if selected_y and selected_y.isdigit() else today.year
    
    selected_months = request.GET.getlist('selected_months')
    if not selected_months:
        selected_months = [str(today.month)]
        
    months_to_show = []
    for m_str in selected_months:
        if m_str.isdigit():
            m_val = int(m_str)
            if 1 <= m_val <= 12:
                months_to_show.append(datetime.date(y_val, m_val, 1))
    months_to_show.sort()
        
    months_choices = [
        (1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'),
        (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'),
        (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December')
    ]
    years_choices = list(range(today.year - 10, today.year + 11))
    
    payment_status = request.GET.getlist('payment_status')
    bill_given = request.GET.getlist('bill_given')
    search_query = request.GET.get('search', '').strip()
    
    villas_query = Villa.objects.all().order_by('-created_at')
    if search_query:
        villas_query = villas_query.filter(name__icontains=search_query)
        
    all_villas = list(villas_query.prefetch_related('payment_records'))
    
    villas = []
    
    for villa in all_villas:
        villa.recent_payments = []
        payment_dict = {p.month_year: p for p in villa.payment_records.all()}
        for m in reversed(months_to_show):
            villa.recent_payments.append({'month': m, 'record': payment_dict.get(m, None)})
            
        villa_matches = False
        
        for m in months_to_show:
            record = payment_dict.get(m, None)

            if not payment_status and not bill_given:
                villa_matches = True
                break

            # A transaction must actually exist in the database
            # when filters are active.
            if record is None:
                continue

            is_paid = record.is_paid
            is_bg = record.bill_given

            match_ps = True
            if payment_status:
                if 'paid' in payment_status and 'not_paid' in payment_status:
                    match_ps = True
                elif 'paid' in payment_status:
                    match_ps = is_paid
                elif 'not_paid' in payment_status:
                    match_ps = not is_paid

            match_bg = True
            if bill_given:
                if 'given' in bill_given and 'not_given' in bill_given:
                    match_bg = True
                elif 'given' in bill_given:
                    match_bg = is_bg
                elif 'not_given' in bill_given:
                    match_bg = not is_bg

            if match_ps and match_bg:
                villa_matches = True
                break
                
        if villa_matches:
            villas.append(villa)

    return render(request, 'cleaning_app/dashboard.html', {
        'villas': villas,
        'months': list(reversed(months_to_show)),  # pass the header months
        'selected_y': y_val,
        'selected_months': selected_months,
        'payment_status': payment_status,
        'bill_given': bill_given,
        'search_query': search_query,
        'months_choices': months_choices,
        'years_choices': years_choices
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
def edit_villa(request, villa_id):
    villa = get_object_or_404(Villa, pk=villa_id)
    if request.method == 'POST':
        form = VillaForm(request.POST, instance=villa)
        if form.is_valid():
            form.save()
            return redirect('villa_detail', villa_id=villa.id)
    else:
        form = VillaForm(instance=villa)
    return render(request, 'cleaning_app/edit_villa.html', {'form': form, 'villa': villa})

@login_required
def delete_villa(request, villa_id):
    villa = get_object_or_404(Villa, pk=villa_id)
    if request.method == 'POST':
        villa.delete()
        return redirect('dashboard')
    return redirect('villa_detail', villa_id=villa.id)

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
        form = PaymentPeriodForm(request.POST)
        if form.is_valid():
            start_month = form.cleaned_data.get('start_month')
            end_month = form.cleaned_data.get('end_month')
            total_amount = form.cleaned_data.get('total_amount', 0)
            
            # Calculate months between start and end inclusive
            months_to_update = []
            curr = start_month
            while curr <= end_month:
                months_to_update.append(curr)
                # Next month
                if curr.month == 12:
                    curr = datetime.date(curr.year + 1, 1, 1)
                else:
                    curr = datetime.date(curr.year, curr.month + 1, 1)
            
            count = len(months_to_update)
            amount_per_month = total_amount / count if count > 0 else 0
            
            # Check for existing records
            existing_records = PaymentRecord.objects.filter(
                villa=villa, 
                month_year__in=months_to_update
            )
            
            confirm_overwrite = request.POST.get('confirm_overwrite') == 'true'
            
            if existing_records.exists() and not confirm_overwrite:
                conflicting_months = [r.month_year.strftime('%B %Y') for r in existing_records]
                messages.warning(request, f"Payments for {', '.join(conflicting_months)} are already logged. Do you want to overwrite them?")
                return render(request, 'cleaning_app/manage_payments.html', {
                    'villa': villa,
                    'payments': payments,
                    'form': form,
                    'conflicting_months': conflicting_months
                })

            for month_date in months_to_update:
                PaymentRecord.objects.update_or_create(
                    villa=villa,
                    month_year=month_date,
                    defaults={
                        'bill_given': form.cleaned_data.get('bill_given'),
                        'amount_paid': amount_per_month,
                        'is_paid': form.cleaned_data.get('is_paid'),
                        'payment_date': form.cleaned_data.get('payment_date'),
                        'received_from': form.cleaned_data.get('received_from'),
                    }
                )
            return redirect('manage_payments', villa_id=villa.id)
    else:
        form = PaymentPeriodForm()

    return render(request, 'cleaning_app/manage_payments.html', {
        'villa': villa,
        'payments': payments,
        'form': form
    })

@login_required
def update_payment(request, payment_id):
    payment = get_object_or_404(PaymentRecord, pk=payment_id)
    if request.method == 'POST':
        form = PaymentRecordForm(request.POST, instance=payment)
        if form.is_valid():
            form.save()
            return redirect('manage_payments', villa_id=payment.villa.id)
    else:
        form = PaymentRecordForm(instance=payment)
    return render(request, 'cleaning_app/payment_detail.html', {'form': form, 'payment': payment})

@login_required
def toggle_dashboard_payment(request, villa_id):
    if request.method == 'POST':
        villa = get_object_or_404(Villa, pk=villa_id)
        action = request.POST.get('action')
        month_str = request.POST.get('month_year')
        
        url = reverse('dashboard')
        query_string = request.GET.urlencode()
        if query_string:
            url += '?' + query_string

        try:
            year, month, day = map(int, month_str.split('-'))
            month_date = datetime.date(year, month, day)
        except:
            return redirect(url)
            
        payment, created = PaymentRecord.objects.get_or_create(
            villa=villa,
            month_year=month_date
        )
        
        if action == 'toggle_bill':
            payment.bill_given = not payment.bill_given
        elif action == 'toggle_paid':
            payment.is_paid = not payment.is_paid
        
        payment.save()
        
        return redirect(url)
        
    return redirect('dashboard')


