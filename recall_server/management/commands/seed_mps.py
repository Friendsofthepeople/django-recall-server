import json
from django.core.management.base import BaseCommand
from recall_server.mps.models import MemberOfParliament

class Command(BaseCommand):
    help = 'Seeds the database with Member of Parliament records from JSON'

    def handle(self, *args, **options):
        # 1. Open and load your JSON data file
        with open('recall_server/management/mps_data/json/representatives.json', 'r', encoding='utf-8') as file:
            mps_data = json.load(file)

        # 2. Map JSON uppercase keys to lowercased Django model fields
        mps_to_create = [
            MemberOfParliament(
                name=mp['NAME'],
                constituency=mp['CONSTITUENCY'],
                party=mp['PARTY'],
                county=""  # Assigned as empty since 'county' is omitted in the JSON data
            )
            for mp in mps_data
        ]

        # 3. Batch commit to the database
        MemberOfParliament.objects.bulk_create(mps_to_create)

        # 4. Use self.stdout for standard Django command output
        self.stdout.write(
            self.style.SUCCESS(f"Successfully populated {len(mps_to_create)} MPs into the database!")
        )
