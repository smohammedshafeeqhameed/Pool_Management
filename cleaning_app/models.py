from django.db import models
from django.contrib.auth.models import User

class Villa(models.Model):
    name = models.CharField(max_length=100)
    address = models.TextField()
    pool_size = models.CharField(max_length=50, blank=True, help_text="e.g., 20x40 feet or 10,000 gallons")
    added_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='villas')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class CleaningRecord(models.Model):
    villa = models.ForeignKey(Villa, on_delete=models.CASCADE, related_name='cleaning_records')
    date = models.DateField()
    cleaner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='cleaning_sessions')
    ph_level = models.FloatField(null=True, blank=True, help_text="pH level (ideal 7.2 - 7.8)")
    chlorine_level = models.FloatField(null=True, blank=True, help_text="Chlorine level in ppm (ideal 1.0 - 3.0)")
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.villa.name} - {self.date}"
