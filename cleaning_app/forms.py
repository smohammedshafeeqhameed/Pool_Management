from django import forms
import datetime
from .models import Villa, PaymentRecord


class VillaForm(forms.ModelForm):
    class Meta:
        model = Villa
        fields = ['name', 'phone_number', 'latitude', 'longitude']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Villa Name'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g., 555-0199'}),
            'latitude': forms.NumberInput(attrs={'class': 'form-input', 'step': 'any', 'placeholder': 'Latitude (e.g., 25.2048)'}),
            'longitude': forms.NumberInput(attrs={'class': 'form-input', 'step': 'any', 'placeholder': 'Longitude (e.g., 55.2708)'}),
        }


class PaymentPeriodForm(forms.Form):
    """Form for logging a payment across a period of months (inclusive)."""
    start_month = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={'class': 'form-input', 'type': 'month'}),
        input_formats=['%Y-%m', '%Y-%m-%d'],
        label="Start Month"
    )
    end_month = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={'class': 'form-input', 'type': 'month'}),
        input_formats=['%Y-%m', '%Y-%m-%d'],
        label="End Month"
    )
    total_amount = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        initial=0,
        widget=forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01', 'placeholder': '0.00'}),
        label="Total Amount (will be divided equally)"
    )
    payment_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
        label="Date Received"
    )
    received_from = forms.CharField(
        required=False,
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Name of payer'})
    )
    STATUS_CHOICES_PAID = [(True, 'Paid'), (False, 'Unpaid')]
    STATUS_CHOICES_BILL = [(True, 'Bill Given'), (False, 'Not Given')]
    
    bill_given = forms.TypedChoiceField(
        choices=STATUS_CHOICES_BILL,
        coerce=lambda x: x == 'True',
        widget=forms.Select(attrs={'class': 'form-input'}),
        label="Bill Status",
        initial=False
    )
    is_paid = forms.TypedChoiceField(
        choices=STATUS_CHOICES_PAID,
        coerce=lambda x: x == 'True',
        widget=forms.Select(attrs={'class': 'form-input'}),
        label="Payment Status",
        initial=False
    )

    def clean_start_month(self):
        d = self.cleaned_data.get('start_month')
        if d:
            return d.replace(day=1)
        return d

    def clean_end_month(self):
        d = self.cleaned_data.get('end_month')
        if d:
            return d.replace(day=1)
        return d
        
    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get('start_month')
        end = cleaned_data.get('end_month')
        
        if start and end and start > end:
            raise forms.ValidationError("End Month cannot be before Start Month.")
            
        return cleaned_data

class PaymentRecordForm(forms.ModelForm):
    bill_given = forms.TypedChoiceField(
        choices=[(True, 'Bill Given'), (False, 'Not Given')],
        coerce=lambda x: x == 'True',
        widget=forms.Select(attrs={'class': 'form-input'}),
        label="Bill Status"
    )
    is_paid = forms.TypedChoiceField(
        choices=[(True, 'Paid'), (False, 'Unpaid')],
        coerce=lambda x: x == 'True',
        widget=forms.Select(attrs={'class': 'form-input'}),
        label="Payment Status"
    )

    class Meta:
        model = PaymentRecord
        fields = ['amount_paid', 'payment_date', 'received_from', 'bill_given', 'is_paid']
        widgets = {
            'amount_paid': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01'}),
            'payment_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'received_from': forms.TextInput(attrs={'class': 'form-input'}),
        }
