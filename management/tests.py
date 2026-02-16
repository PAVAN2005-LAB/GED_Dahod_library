from django.test import TestCase, Client
from django.utils import timezone
from datetime import timedelta
from .models import Student, Book, LibraryLog, Transaction


class StudentModelTest(TestCase):
    """Test Student model CRUD and string representation."""

    def setUp(self):
        self.student = Student.objects.create(
            enrollment_id='STU-001',
            name='Pavan Kumar',
            email='pavan@college.edu',
            department='Computer Science'
        )

    def test_student_creation(self):
        self.assertEqual(self.student.enrollment_id, 'STU-001')
        self.assertEqual(self.student.name, 'Pavan Kumar')

    def test_student_str(self):
        self.assertEqual(str(self.student), 'Pavan Kumar (STU-001)')


class BookModelTest(TestCase):
    """Test Book model defaults and relationships."""

    def setUp(self):
        self.book = Book.objects.create(
            book_id='BK-101',
            title='Clean Code',
            shelf_location='A-1'
        )

    def test_book_default_status(self):
        self.assertEqual(self.book.status, 'Available')

    def test_book_no_holder_by_default(self):
        self.assertIsNone(self.book.current_holder)

    def test_book_str(self):
        self.assertEqual(str(self.book), 'Clean Code (BK-101)')


class LibraryLogModelTest(TestCase):
    """Test LibraryLog entry/exit logic."""

    def setUp(self):
        self.student = Student.objects.create(
            enrollment_id='STU-001',
            name='Pavan Kumar',
            email='pavan@college.edu',
            department='CSE'
        )

    def test_log_is_inside_on_entry(self):
        log = LibraryLog.objects.create(student=self.student)
        self.assertTrue(log.is_inside)
        self.assertIsNone(log.exit_time)

    def test_log_is_not_inside_on_exit(self):
        log = LibraryLog.objects.create(student=self.student)
        log.exit_time = timezone.now()
        log.save()
        self.assertFalse(log.is_inside)


class TransactionModelTest(TestCase):
    """Test Transaction auto due-date and overdue logic."""

    def setUp(self):
        self.student = Student.objects.create(
            enrollment_id='STU-001',
            name='Pavan Kumar',
            email='pavan@college.edu',
            department='CSE'
        )
        self.book = Book.objects.create(
            book_id='BK-101',
            title='Clean Code',
            shelf_location='A-1'
        )

    def test_auto_due_date(self):
        tx = Transaction(student=self.student, book=self.book)
        tx.save()
        self.assertIsNotNone(tx.due_date)
        # Due date should be ~14 days from now
        expected = timezone.now() + timedelta(days=14)
        self.assertAlmostEqual(
            tx.due_date.timestamp(),
            expected.timestamp(),
            delta=5  # within 5 seconds
        )

    def test_is_overdue_false_when_returned(self):
        tx = Transaction(student=self.student, book=self.book, returned=True)
        tx.due_date = timezone.now() - timedelta(days=1)  # past due
        tx.save()
        self.assertFalse(tx.is_overdue)

    def test_is_overdue_true_when_past_due(self):
        tx = Transaction(student=self.student, book=self.book)
        tx.due_date = timezone.now() - timedelta(days=1)
        tx.save()
        self.assertTrue(tx.is_overdue)


class KioskViewTest(TestCase):
    """Test the Kiosk check-in/check-out flow."""

    def setUp(self):
        self.client = Client()
        self.student = Student.objects.create(
            enrollment_id='STU-001',
            name='Pavan Kumar',
            email='pavan@college.edu',
            department='CSE'
        )

    def test_kiosk_get(self):
        response = self.client.get('/kiosk/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Library Kiosk')

    def test_kiosk_checkin(self):
        response = self.client.post('/kiosk/', {'barcode': 'STU-001'})
        self.assertEqual(response.status_code, 302)
        # Student should now be inside
        log = LibraryLog.objects.filter(student=self.student, exit_time__isnull=True).last()
        self.assertIsNotNone(log)

    def test_kiosk_checkout(self):
        # First check-in
        LibraryLog.objects.create(student=self.student)
        # Then check-out
        response = self.client.post('/kiosk/', {'barcode': 'STU-001'})
        self.assertEqual(response.status_code, 302)
        log = LibraryLog.objects.filter(student=self.student).last()
        self.assertIsNotNone(log.exit_time)

    def test_kiosk_unknown_barcode(self):
        response = self.client.post('/kiosk/', {'barcode': 'UNKNOWN-999'}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'not found')

    def test_kiosk_empty_barcode(self):
        response = self.client.post('/kiosk/', {'barcode': ''}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No barcode')

    def test_kiosk_invalid_barcode(self):
        response = self.client.post('/kiosk/', {'barcode': '<script>alert(1)</script>'}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid barcode')


class DashboardViewTest(TestCase):
    """Test dashboard requires authentication."""

    def setUp(self):
        self.client = Client()

    def test_dashboard_requires_login(self):
        response = self.client.get('/dashboard/')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/login/', response.url)

    def test_export_requires_login(self):
        response = self.client.get('/export/')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/login/', response.url)


class ExportViewTest(TestCase):
    """Test export functionality for authenticated users."""

    def setUp(self):
        from django.contrib.auth.models import User
        self.admin = User.objects.create_superuser('admin', 'admin@test.com', 'testpass123')
        self.client = Client()
        self.client.login(username='admin', password='testpass123')

    def test_export_empty_redirects(self):
        response = self.client.get('/export/')
        self.assertEqual(response.status_code, 302)  # redirect back due to no data

    def test_export_with_data(self):
        student = Student.objects.create(
            enrollment_id='STU-001',
            name='Pavan Kumar',
            email='pavan@college.edu',
            department='CSE'
        )
        LibraryLog.objects.create(student=student)
        response = self.client.get('/export/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response['Content-Type'],
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
