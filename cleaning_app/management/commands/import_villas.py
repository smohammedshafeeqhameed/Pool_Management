import os
import pdfplumber
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from cleaning_app.models import Villa
from django.conf import settings

class Command(BaseCommand):
    help = 'Imports villas from a PDF file'

    def handle(self, *args, **kwargs):
        pdf_path = os.path.join(settings.BASE_DIR, 'Villa.pdf')
        if not os.path.exists(pdf_path):
            self.stdout.write(self.style.ERROR(f'PDF not found at {pdf_path}'))
            return

        # Fetch the first user to assign as added_by
        user = User.objects.first()
        if not user:
            self.stdout.write(self.style.ERROR('No users found in the database. Please create a user first.'))
            return

        self.stdout.write(self.style.SUCCESS(f'Using user {user.username} as added_by'))

        villas_added = 0
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()
                if not tables:
                    continue
                
                for table in tables:
                    for i, row in enumerate(table):
                        # Skip header row if it contains 'Villa Name'
                        if i == 0 and row and row[0] and 'Villa Name' in str(row[0]):
                            continue
                        
                        if not row or not row[0]:
                            continue
                        
                        villa_name = str(row[0]).strip()
                        if villa_name:
                            # Create the villa if it doesn't exist
                            villa, created = Villa.objects.get_or_create(
                                name=villa_name,
                                defaults={'added_by': user}
                            )
                            if created:
                                self.stdout.write(self.style.SUCCESS(f'Added: {villa_name}'))
                                villas_added += 1
                            else:
                                self.stdout.write(self.style.WARNING(f'Already exists: {villa_name}'))

        self.stdout.write(self.style.SUCCESS(f'Successfully imported {villas_added} new villas.'))
