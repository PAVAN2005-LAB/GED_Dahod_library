from django.contrib import admin
from django.contrib.auth.models import User, Group
from .models import Student, Book, LibraryLog, Transaction
from django.utils import timezone
from datetime import timedelta


# ── Inject live stats into the admin index context ──────────────
_original_index = admin.AdminSite.index

def _index_with_stats(self, request, extra_context=None):
    from .models import Student, Book, LibraryLog, Transaction, RenewRequest
    extra_context = extra_context or {}
    extra_context['stats'] = {
        'total_students':   Student.objects.count(),
        'total_books':      Book.objects.count(),
        'books_available':  Book.objects.filter(status='Available').count(),
        'books_issued':     Book.objects.filter(status='Issued').count(),
        'inside_now':       LibraryLog.objects.filter(exit_time__isnull=True).count(),
        'overdue':          Transaction.objects.filter(returned=False, due_date__lt=timezone.now()).count(),
        'pending_renewals': RenewRequest.objects.filter(status='Pending').count(),
    }
    return _original_index(self, request, extra_context=extra_context)

admin.AdminSite.index = _index_with_stats


# ── Admin Site Branding ────────────────────────────────────
admin.site.site_header = 'GECDahod Library'
admin.site.site_title = 'GECDahod Library Admin'
admin.site.index_title = 'Library Management Panel'


# ── Student Admin ───────────────────────────────────────────
@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('enrollment_id', 'name', 'email', 'mobile_no', 'department')
    search_fields = ('enrollment_id', 'name', 'email', 'mobile_no')
    list_filter = ('department',)
    list_per_page = 25


# ── Book Admin ──────────────────────────────────────────────
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('access_code', 'title', 'isbn_no', 'author', 'edition', 'allocated_department', 'status', 'current_holder')
    list_filter = ('status', 'allocated_department', 'shelf_location')
    search_fields = ('access_code', 'title', 'author', 'isbn_no')
    list_per_page = 25


# ── Library Log Admin ───────────────────────────────────────
@admin.register(LibraryLog)
class LibraryLogAdmin(admin.ModelAdmin):
    list_display = ('student', 'entry_time', 'exit_time', 'duration_display', 'is_inside')
    list_filter = ('entry_time', 'exit_time')
    search_fields = ('student__name', 'student__enrollment_id')
    readonly_fields = ('entry_time',)
    autocomplete_fields = ['student']
    list_per_page = 25
    actions = []

    @admin.display(boolean=True, description='Currently Inside')
    def is_inside(self, obj):
        return obj.is_inside

    @admin.display(description='Duration')
    def duration_display(self, obj):
        if obj.exit_time:
            duration = obj.exit_time - obj.entry_time
            hours, remainder = divmod(int(duration.total_seconds()), 3600)
            minutes, _ = divmod(remainder, 60)
            return f'{hours}h {minutes}m'
        return '—'


# ── Transaction Admin ───────────────────────────────────────
@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('student', 'book', 'issue_date', 'due_date', 'returned', 'is_overdue_display')
    list_filter = ('returned', 'issue_date', 'due_date')
    search_fields = ('student__name', 'student__enrollment_id', 'book__title', 'book__access_code')
    readonly_fields = ('issue_date',)
    autocomplete_fields = ['student', 'book']
    list_per_page = 25
    actions = ['mark_returned']

    def get_changeform_initial_data(self, request):
        """Pre-fill due_date with 15 days from now."""
        from django.utils import timezone
        from datetime import timedelta
        initial = super().get_changeform_initial_data(request)
        initial['due_date'] = timezone.now() + timedelta(days=15)
        return initial

    @admin.display(boolean=True, description='Overdue')
    def is_overdue_display(self, obj):
        return obj.is_overdue

    @admin.action(description='✅ Mark selected as returned')
    def mark_returned(self, request, queryset):
        updated = queryset.filter(returned=False).update(returned=True)
        self.message_user(request, f'{updated} transaction(s) marked as returned.')

from .models import RenewRequest
from django.utils import timezone
from datetime import timedelta

@admin.register(RenewRequest)
class RenewRequestAdmin(admin.ModelAdmin):
    list_display = ('transaction', 'request_date', 'status', 'current_due_date')
    list_filter = ('status', 'request_date')
    search_fields = ('transaction__student__enrollment_id', 'transaction__book__access_code')
    actions = ['approve_requests']

    def current_due_date(self, obj):
        return obj.transaction.due_date

    @admin.action(description='👍 Approve selected renew requests (+15 days)')
    def approve_requests(self, request, queryset):
        for req in queryset.filter(status='Pending'):
            # Update the underlying transaction due_date
            req.transaction.due_date = timezone.now() + timedelta(days=15)
            req.transaction.save()
            # Update the request status
            req.status = 'Approved'
            req.save()
        self.message_user(request, 'Selected requests have been approved and due dates extended.')

from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import ManualReminderProxy

@admin.register(ManualReminderProxy)
class ManualReminderProxyAdmin(admin.ModelAdmin):
    def changelist_view(self, request, extra_context=None):
        # Redirect directly to our custom manual reminder view
        return HttpResponseRedirect(reverse('admin_manual_reminder'))

