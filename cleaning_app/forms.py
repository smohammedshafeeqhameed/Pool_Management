from django import forms
from .models import Villa, CleaningRecord, PaymentRecord

class VillaForm(forms.ModelForm):
    class Meta:
        model = Villa
        fields = ['name', 'address', 'pool_size']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Villa Name'}),
            'address': forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Address'}),
            'pool_size': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g., 20x40 feet'}),
        }

class CleaningRecordForm(forms.ModelForm):
    class Meta:
        model = CleaningRecord
        fields = ['date', 'ph_level', 'chlorine_level', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'ph_level': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.1'}),
            'chlorine_level': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.1'}),
            'notes': forms.Textarea(attrs={'class': 'form-input', 'rows': 3}),
        }

class PaymentRecordForm(forms.ModelForm):
    class Meta:
        model = PaymentRecord
        fields = ['month_year', 'bill_given', 'amount_paid', 'is_paid']
        widgets = {
            'month_year': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'amount_paid': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01'}),
        }
