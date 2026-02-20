import io
import pandas as pd
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
from django.template.response import TemplateResponse
from django.utils import timezone
from .models import Student, LibraryLog, Transaction


@staff_member_required(login_url='/admin/login/')
def reports_dashboard(request):
    """Custom Reports Dashboard inside admin."""
    departments = [c[0] for c in Student.DEPARTMENT_CHOICES]
    context = {
        'title': 'Download Reports',
        'departments': departments,
        'is_nav_sidebar_enabled': True,
        'site_header': '📚 Smart College Library',
        'has_permission': True,
    }
    return TemplateResponse(request, 'admin/reports_dashboard.html', context)


@staff_member_required(login_url='/admin/login/')
@staff_member_required(login_url='/admin/login/')
def download_entry_exit(request):
    """Download filtered Entry-Exit report with duration."""
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    department = request.GET.get('department', '')

    queryset = LibraryLog.objects.select_related('student').all()

    if date_from:
        queryset = queryset.filter(entry_time__date__gte=date_from)
    if date_to:
        queryset = queryset.filter(entry_time__date__lte=date_to)
    if department:
        queryset = queryset.filter(student__department=department)

    rows = []
    for log in queryset.order_by('-entry_time'):
        if log.exit_time:
            duration = log.exit_time - log.entry_time
            hours, remainder = divmod(int(duration.total_seconds()), 3600)
            minutes, seconds = divmod(remainder, 60)
            duration_str = f'{hours}h {minutes}m {seconds}s'
        else:
            duration_str = 'Still Inside'

        rows.append({
            'enrollment_id': log.student.enrollment_id,
            'name': log.student.name,
            'department': log.student.department,
            'mobile_no': log.student.mobile_no,
            'entry_time': log.entry_time.strftime('%Y-%m-%d %H:%M:%S'),
            'exit_time': log.exit_time.strftime('%Y-%m-%d %H:%M:%S') if log.exit_time else 'Still Inside',
            'duration': duration_str,
        })

    df = pd.DataFrame(rows)
    if df.empty:
        df = pd.DataFrame(columns=[
            'Enrollment ID', 'Name', 'Department', 'Mobile No',
            'Entry Time', 'Exit Time', 'Duration'
        ])
    else:
        df.columns = [
            'Enrollment ID', 'Name', 'Department', 'Mobile No',
            'Entry Time', 'Exit Time', 'Duration'
        ]

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Entry-Exit Report')
    output.seek(0)

    timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
    response = HttpResponse(
        output,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="entry_exit_report_{timestamp}.xlsx"'
    return response


@staff_member_required(login_url='/admin/login/')
def download_book_issues(request):
    """Download filtered Book Issue report."""
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    department = request.GET.get('department', '')
    status = request.GET.get('status', '')

    queryset = Transaction.objects.select_related('student', 'book').all()

    if date_from:
        queryset = queryset.filter(issue_date__date__gte=date_from)
    if date_to:
        queryset = queryset.filter(issue_date__date__lte=date_to)
    if department:
        queryset = queryset.filter(student__department=department)
    
    if status == 'returned':
        queryset = queryset.filter(returned=True)
    elif status == 'pending':
        queryset = queryset.filter(returned=False)
    elif status == 'overdue':
        queryset = queryset.filter(returned=False, due_date__lt=timezone.now())

    rows = []
    now = timezone.now()
    for tx in queryset.order_by('-issue_date'):
        if tx.returned:
            book_status = 'Returned'
        elif now > tx.due_date:
            book_status = f'OVERDUE ({(now - tx.due_date).days} days)'
        else:
            book_status = 'Pending'

        rows.append({
            'enrollment_id': tx.student.enrollment_id,
            'name': tx.student.name,
            'department': tx.student.department,
            'access_code': tx.book.access_code,
            'book_title': tx.book.title,
            'book_author': tx.book.author or '',
            'shelf_location': tx.book.shelf_location,
            'issue_date': tx.issue_date.strftime('%Y-%m-%d'),
            'due_date': tx.due_date.strftime('%Y-%m-%d'),
            'status': book_status,
        })

    df = pd.DataFrame(rows)
    if df.empty:
        df = pd.DataFrame(columns=[
            'Enrollment ID', 'Student Name', 'Department',
            'Access Code', 'Book Title', 'Author', 'Shelf Location',
            'Issue Date', 'Due Date', 'Status'
        ])
    else:
        df.columns = [
            'Enrollment ID', 'Student Name', 'Department',
            'Access Code', 'Book Title', 'Author', 'Shelf Location',
            'Issue Date', 'Due Date', 'Status'
        ]

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Book Issues Report')
    output.seek(0)

    timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
    response = HttpResponse(
        output,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="book_issues_report_{timestamp}.xlsx"'
    return response


@staff_member_required(login_url='/admin/login/')
def download_overdue_students(request):
    """Download Overdue Students report."""
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    department = request.GET.get('department', '')

    queryset = Transaction.objects.select_related('student', 'book').filter(
        returned=False,
        due_date__lt=timezone.now()
    )

    if date_from:
        queryset = queryset.filter(issue_date__date__gte=date_from)
    if date_to:
        queryset = queryset.filter(issue_date__date__lte=date_to)
    if department:
        queryset = queryset.filter(student__department=department)

    rows = []
    now = timezone.now()
    for tx in queryset.order_by('due_date'):
        overdue_days = (now - tx.due_date).days
        rows.append({
            'enrollment_id': tx.student.enrollment_id,
            'name': tx.student.name,
            'department': tx.student.department,
            'mobile_no': tx.student.mobile_no,
            'book_title': tx.book.title,
            'book_author': tx.book.author or '',
            'access_code': tx.book.access_code,
            'due_date': tx.due_date.strftime('%Y-%m-%d'),
            'overdue_days': overdue_days,
        })

    if not rows:
        df = pd.DataFrame(columns=[
            'Enrollment ID', 'Student Name', 'Department', 'Mobile No',
            'Book Title', 'Author', 'Access Code', 'Due Date', 'Overdue Days'
        ])
    else:
        df = pd.DataFrame(rows)
        df.columns = [
            'Enrollment ID', 'Student Name', 'Department', 'Mobile No',
            'Book Title', 'Author', 'Access Code', 'Due Date', 'Overdue Days'
        ]

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Overdue Students')
    output.seek(0)

    timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
    response = HttpResponse(
        output,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="overdue_students_report_{timestamp}.xlsx"'
    return response
