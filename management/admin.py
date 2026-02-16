from django.contrib import admin
from django.contrib.auth.models import User, Group
from .models import Student, Book, LibraryLog, Transaction


# ── Unregister clutter ──────────────────────────────────────
admin.site.unregister(Group)
admin.site.unregister(User)

# ── Customize Admin Site Branding ───────────────────────────
admin.site.site_header = '📚 GECDahod Library'
admin.site.site_title = 'GECDahod Library Admin'
admin.site.index_title = 'Library Management Panel'


# ── Student Admin ───────────────────────────────────────────
@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('enrollment_id', 'name', 'email', 'mobile_no', 'department', 'semester')
    search_fields = ('enrollment_id', 'name', 'email', 'mobile_no')
    list_filter = ('department', 'semester')
    list_per_page = 25


# ── Book Admin ──────────────────────────────────────────────
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('book_id', 'title', 'shelf_location', 'status', 'current_holder')
    list_filter = ('status', 'shelf_location')
    search_fields = ('book_id', 'title')
    list_per_page = 25


# ── Library Log Admin ───────────────────────────────────────
@admin.register(LibraryLog)
class LibraryLogAdmin(admin.ModelAdmin):
    list_display = ('student', 'entry_time', 'exit_time', 'duration_display', 'is_inside')
    list_filter = ('entry_time', 'exit_time')
    search_fields = ('student__name', 'student__enrollment_id')
    readonly_fields = ('entry_time',)
    list_per_page = 25

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
    search_fields = ('student__name', 'student__enrollment_id', 'book__title', 'book__book_id')
    readonly_fields = ('issue_date',)
    list_per_page = 25
    actions = ['mark_returned']

    @admin.display(boolean=True, description='Overdue')
    def is_overdue_display(self, obj):
        return obj.is_overdue

    @admin.action(description='✅ Mark selected as returned')
    def mark_returned(self, request, queryset):
        updated = queryset.filter(returned=False).update(returned=True)
        self.message_user(request, f'{updated} transaction(s) marked as returned.')
