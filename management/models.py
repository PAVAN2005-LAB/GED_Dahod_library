from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator
from datetime import timedelta


class Student(models.Model):
    """Represents a student registered in the library system."""
    enrollment_id = models.CharField(
        max_length=50,
        primary_key=True,
        validators=[RegexValidator(
            regex=r'^[A-Za-z0-9_-]+$',
            message='Enrollment ID must contain only alphanumeric characters, hyphens, or underscores.'
        )],
        help_text='Unique barcode/enrollment ID for the student.'
    )
    SEMESTER_CHOICES = [(i, f'Semester {i}') for i in range(1, 9)]
    DEPARTMENT_CHOICES = [
        ('Computer', 'Computer'),
        ('EC', 'EC'),
        ('Civil', 'Civil'),
        ('Electrical', 'Electrical'),
        ('Mechanical', 'Mechanical'),
    ]

    name = models.CharField(max_length=100)
    email = models.EmailField()
    mobile_no = models.CharField(
        max_length=15,
        validators=[RegexValidator(
            regex=r'^\d{10}$',
            message='Enter a valid 10-digit mobile number.'
        )],
        help_text='10-digit mobile number'
    )
    department = models.CharField(max_length=100, choices=DEPARTMENT_CHOICES)
    semester = models.IntegerField(choices=SEMESTER_CHOICES, default=1, help_text='Current semester (1–8)')

    class Meta:
        ordering = ['name']
        verbose_name = 'Student'
        verbose_name_plural = 'Students'

    def __str__(self):
        return f"{self.name} ({self.enrollment_id})"


class Book(models.Model):
    """Represents a book in the library inventory."""
    STATUS_CHOICES = [
        ('Available', 'Available'),
        ('Issued', 'Issued'),
    ]
    book_id = models.CharField(
        max_length=50,
        primary_key=True,
        validators=[RegexValidator(
            regex=r'^[A-Za-z0-9_-]+$',
            message='Book ID must contain only alphanumeric characters, hyphens, or underscores.'
        )],
        help_text='Unique barcode ID for the book.'
    )
    title = models.CharField(max_length=200)
    shelf_location = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Available')
    current_holder = models.ForeignKey(
        Student,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='held_books',
        help_text='Student who currently holds this book.'
    )

    class Meta:
        ordering = ['title']
        verbose_name = 'Book'
        verbose_name_plural = 'Books'

    def __str__(self):
        return f"{self.title} ({self.book_id})"


class LibraryLog(models.Model):
    """Tracks student entry/exit from the physical library."""
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='library_logs'
    )
    entry_time = models.DateTimeField(auto_now_add=True, db_index=True)
    exit_time = models.DateTimeField(null=True, blank=True, db_index=True)

    class Meta:
        ordering = ['-entry_time']
        verbose_name = 'Library Log'
        verbose_name_plural = 'Library Logs'
        indexes = [
            models.Index(fields=['student', 'exit_time'], name='idx_student_exit'),
        ]

    @property
    def is_inside(self):
        return self.exit_time is None

    def __str__(self):
        status = "Inside" if self.is_inside else "Exited"
        return f"{self.student.name} - {self.entry_time:%Y-%m-%d %H:%M} ({status})"


class Transaction(models.Model):
    """Tracks book issue/return transactions."""
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='transactions'
    )
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name='transactions'
    )
    issue_date = models.DateTimeField(auto_now_add=True, db_index=True)
    due_date = models.DateTimeField(db_index=True)
    returned = models.BooleanField(default=False, help_text='Has the book been returned?')

    class Meta:
        ordering = ['-issue_date']
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transactions'

    def save(self, *args, **kwargs):
        # Auto-set due_date to 14 days from now on first creation
        if not self.pk and not self.due_date:
            self.due_date = timezone.now() + timedelta(days=14)
        super().save(*args, **kwargs)

    @property
    def is_overdue(self):
        return not self.returned and timezone.now() > self.due_date

    def __str__(self):
        return f"{self.student.name} borrowed {self.book.title}"
