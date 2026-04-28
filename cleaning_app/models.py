from django.db import models
from django.contrib.auth.models import User

class Villa(models.Model):
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15, blank=True, unique=True, help_text="Contact phone number")
    location = models.CharField(max_length=255, blank=True, null=True, help_text="Location details")

    
    service_start = models.DateField(null=True, blank=True, help_text="First billing month (1st of month)") #unused
    service_end = models.DateField(null=True, blank=True, help_text="Last billing month (1st of month)") #unused
    added_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='villas')
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.name




class PaymentRecord(models.Model):
    villa = models.ForeignKey(Villa, on_delete=models.CASCADE, related_name='payment_records')
    month_year = models.DateField(help_text="First day of the month representing the billing period")
    bill_given = models.BooleanField(default=False)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_paid = models.BooleanField(default=False)
    payment_date = models.DateField(null=True, blank=True, help_text="Date when the payment was actually received")
    bill_given_date = models.DateField(null=True, blank=True, help_text="Date when the bill was given")
    received_from = models.CharField(max_length=100, blank=True, help_text="Name of the person who made the payment")
    mode_of_payment = models.CharField(max_length=20, choices=[('Cash', 'Cash'), ('Online', 'Online')], blank=True, null=True, help_text="Mode of payment", default='Cash')
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        unique_together = ('villa', 'month_year')
        ordering = ['-month_year']

    def save(self, *args, **kwargs):
        if self.month_year:
            self.month_year = self.month_year.replace(day=1)
            
        import datetime
        if self.is_paid and not self.payment_date:
            self.payment_date = datetime.date.today()
        elif not self.is_paid:
            self.payment_date = None
            
        if self.bill_given and not self.bill_given_date:
            self.bill_given_date = datetime.date.today()
        elif not self.bill_given:
            self.bill_given_date = None
            
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.villa.name} - {self.month_year.strftime('%B %Y')}"

