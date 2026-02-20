import csv
import os
from django.core.management.base import BaseCommand
from management.models import Student, Book

class Command(BaseCommand):
    help = 'Import Students or Books from a CSV file.'

    def add_arguments(self, parser):
        parser.add_argument('type', type=str, choices=['students', 'books'], help='Type of data to import')
        parser.add_argument('file_path', type=str, help='Absolute path to the CSV file')

    def handle(self, *args, **options):
        data_type = options['type']
        file_path = options['file_path']

        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f'File "{file_path}" does not exist.'))
            return

        if data_type == 'students':
            self.import_students(file_path)
        else:
            self.import_books(file_path)

    def import_students(self, file_path):
        """
        Expected CSV: enrollment_id, name, email, mobile_no, department
        """
        self.stdout.write('Starting Student import...')
        count = 0
        students_to_create = []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Basic validation
                eid = row.get('enrollment_id', '').strip()
                if not eid:
                    continue
                
                # Check for duplicates to avoid integrity errors
                if Student.objects.filter(enrollment_id=eid).exists():
                    self.stdout.write(self.style.WARNING(f'Skipping duplicate student: {eid}'))
                    continue

                students_to_create.append(Student(
                    enrollment_id=eid,
                    name=row.get('name', '').strip(),
                    email=row.get('email', '').strip(),
                    mobile_no=row.get('mobile_no', '').strip(),
                    department=row.get('department', 'Computer').strip()
                ))
                count += 1
                
                # Batch processing
                if len(students_to_create) >= 100:
                    Student.objects.bulk_create(students_to_create)
                    students_to_create = []

        if students_to_create:
            Student.objects.bulk_create(students_to_create)

        self.stdout.write(self.style.SUCCESS(f'Successfully imported {count} students.'))

    def import_books(self, file_path):
        """
        Expected CSV: access_code, title, author, shelf_location
        """
        self.stdout.write('Starting Book import...')
        count = 0
        books_to_create = []

        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Basic validation
                # Note: access_code in CSV maps to book_id in database
                acid = row.get('access_code', '').strip()
                if not acid:
                    continue

                if Book.objects.filter(access_code=acid).exists():
                    self.stdout.write(self.style.WARNING(f'Skipping duplicate book: {acid}'))
                    continue

                books_to_create.append(Book(
                    access_code=acid,
                    title=row.get('title', '').strip(),
                    author=row.get('author', '').strip(),
                    shelf_location=row.get('shelf_location', 'General').strip(),
                    status='Available'
                ))
                count += 1

                # Batch processing for large datasets
                if len(books_to_create) >= 500:
                    Book.objects.bulk_create(books_to_create)
                    books_to_create = []
                    self.stdout.write(f'Imported {count} so far...')

        if books_to_create:
            Book.objects.bulk_create(books_to_create)

        self.stdout.write(self.style.SUCCESS(f'Successfully imported {count} books.'))
