import logging
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_http_methods, require_GET
from django.db.models import Q
from .models import Student, LibraryLog, Book
from django.utils import timezone

logger = logging.getLogger('management')


@require_http_methods(["GET", "POST"])
def kiosk(request):
    """Kiosk scanner endpoint — handles student check-in/check-out."""
    if request.method == "POST":
        barcode = request.POST.get('barcode', '').strip()
        
        if not barcode:
            messages.error(request, "⚠️ Input Error: No barcode detected. Please scan again.")
            return redirect('kiosk')
        
        # Sanitize: only allow alphanumeric, hyphens, underscores
        if not barcode.replace('-', '').replace('_', '').isalnum():
            messages.error(request, "⚠️ Format Error: Invalid barcode format. Only alphanumeric characters allowed.")
            return redirect('kiosk')

        try:
            student = Student.objects.get(enrollment_id=barcode)
            log = LibraryLog.objects.filter(
                student=student,
                exit_time__isnull=True
            ).last()

            if log:
                log.exit_time = timezone.now()
                log.save(update_fields=['exit_time'])
                messages.success(request, f" Goodbye, {student.name}! See you next time.")
                logger.info("Student %s checked OUT", student.enrollment_id)
            else:
                LibraryLog.objects.create(student=student)
                messages.success(request, f"Welcome, {student.name}! Access Granted.")
                logger.info("Student %s checked IN", student.enrollment_id)
                
        except Student.DoesNotExist:
            messages.error(request, f" Access Denied: Student ID '{barcode}' not found or not registered.")
            logger.warning("Unknown barcode scanned: %s", barcode)

        return redirect('kiosk')

    return render(request, 'management/kiosk.html')


@require_GET
def dashboard(request):
    """Public dashboard showing who is currently in the library."""
    live_logs = (
        LibraryLog.objects
        .filter(exit_time__isnull=True)
        .select_related('student')
        .order_by('-entry_time')
    )
    total_visits = LibraryLog.objects.count()
    
    today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_visits = LibraryLog.objects.filter(entry_time__gte=today_start).count()
    
    context = {
        'live_logs': live_logs,
        'total_visits': total_visits,
        'today_visits': today_visits,
    }
    return render(request, 'management/dashboard.html', context)


from .models import Transaction, RenewRequest

@require_http_methods(["GET", "POST"])
def renew_request(request):
    """Public portal for students to request book renewals."""
    context = {}
    if request.method == "POST":
        action = request.POST.get("action")
        enrollment_id = request.POST.get("enrollment_id", "").strip()
        access_code = request.POST.get("access_code", "").strip()

        if not enrollment_id or not access_code:
            messages.error(request, "Please provide both Enrollment No. and Book Accession Code.")
            return render(request, "management/renew_book.html", context)

        # Look up active transaction
        transaction = Transaction.objects.filter(
            student__enrollment_id=enrollment_id,
            book__access_code=access_code,
            returned=False
        ).select_related('student', 'book').first()

        if not transaction:
            messages.error(request, "No active issued book found for these details. You may have entered them incorrectly or the book is already returned.")
            return render(request, "management/renew_book.html", {"enrollment_id": enrollment_id, "access_code": access_code})

        if action == "lookup":
            # Check if a pending request already exists
            pending_request = RenewRequest.objects.filter(transaction=transaction, status='Pending').exists()
            context.update({
                "transaction": transaction,
                "pending_request": pending_request,
                "enrollment_id": enrollment_id,
                "access_code": access_code
            })

        elif action == "submit":
            # Prevent duplicate pending requests
            if RenewRequest.objects.filter(transaction=transaction, status='Pending').exists():
                messages.error(request, "You already have a pending renewal request for this book.")
            else:
                RenewRequest.objects.create(transaction=transaction)
                messages.success(request, f"Renewal request for '{transaction.book.title}' sent to Admin successfully!")
            return redirect('renew_request')

    return render(request, 'management/renew_book.html', context)


from .models import Book

@require_http_methods(["GET", "POST"])
def issue_book_manual(request):
    """Manual book issuing using just enrollment number and book access code."""
    context = {}
    if request.method == "POST":
        enrollment_id = request.POST.get("enrollment_id", "").strip()
        access_code = request.POST.get("access_code", "").strip()
        
        if not enrollment_id or not access_code:
            messages.error(request, "Please provide both Enrollment No. and Book Accession Code.")
            return render(request, "management/issue_book.html", context)
            
        try:
            student = Student.objects.get(enrollment_id=enrollment_id)
        except Student.DoesNotExist:
            messages.error(request, f"Student with Enrollment No. '{enrollment_id}' not found.")
            return render(request, "management/issue_book.html", {"enrollment_id": enrollment_id, "access_code": access_code})
            
        try:
            book = Book.objects.get(access_code=access_code)
        except Book.DoesNotExist:
            messages.error(request, f"Book with Accession Code '{access_code}' not found.")
            return render(request, "management/issue_book.html", {"enrollment_id": enrollment_id, "access_code": access_code})

        # ── CASE 1: This exact student already holds this exact book ────────
        # → Suggest renewal instead of issuing again
        own_active_issue = Transaction.objects.filter(
            student=student, book=book, returned=False
        ).select_related('student', 'book').first()

        if own_active_issue:
            return render(request, "management/issue_book.html", {
                "enrollment_id": enrollment_id,
                "access_code": access_code,
                "own_active_issue": own_active_issue,   # triggers renewal-suggestion box in template
            })

        # ── CASE 2: Book is issued to a DIFFERENT student ────────────────────
        other_active_issue = Transaction.objects.filter(book=book, returned=False).first()
        if other_active_issue:
            messages.error(
                request,
                f"This book is currently issued to "
                f"{other_active_issue.student.name} "
                f"(Enrollment: {other_active_issue.student.enrollment_id}). "
                f"It must be returned before it can be issued again."
            )
            return render(request, "management/issue_book.html", {
                "enrollment_id": enrollment_id,
                "access_code": access_code,
            })
            
        # ── CASE 3: Book is free — issue it ─────────────────────────────────
        Transaction.objects.create(student=student, book=book)
        messages.success(request, f"Book '{book.title}' successfully issued to {student.name}.")
        return redirect('issue_book_manual')

    return render(request, 'management/issue_book.html', context)



from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings

@staff_member_required(login_url='/admin/login/')
@require_http_methods(["GET", "POST"])
def admin_manual_reminder(request):
    """Admin page to manually trigger a due reminder for a specific student."""
    context = {
        'title': 'Send Manual Due Reminder',
        'is_nav_sidebar_enabled': True,
        'site_header': ' Smart College Library',
        'has_permission': True,
    }

    if request.method == "POST":
        enrollment_id = request.POST.get("enrollment_id", "").strip()
        if not enrollment_id:
            messages.error(request, "Please provide an Enrollment Number.")
            return render(request, "admin/manual_reminder.html", context)

        try:
            student = Student.objects.get(enrollment_id=enrollment_id)
        except Student.DoesNotExist:
            messages.error(request, f"Student with Enrollment No. '{enrollment_id}' not found.")
            return render(request, "admin/manual_reminder.html", context)

        active_txs = Transaction.objects.filter(student=student, returned=False).select_related('book')
        if not active_txs.exists():
            messages.warning(request, f"{student.name} has no pending books to return.")
            return render(request, "admin/manual_reminder.html", context)

        sent_count = 0
        for tx in active_txs:
            # Build template context
            email_context = {
                'student_name': tx.student.name,
                'enrollment_id': tx.student.enrollment_id,
                'book_title': tx.book.title,
                'access_code': tx.book.access_code,
                'shelf_location': tx.book.shelf_location,
                'issue_date': tx.issue_date.strftime('%d %b, %Y'),
                'due_date': tx.due_date.strftime('%d %b, %Y'),
            }
            subject = f"📚 Library Reminder: Return '{tx.book.title}'"
            text_body = render_to_string('management/email/reminder.txt', email_context)
            html_body = render_to_string('management/email/reminder.html', email_context)

            try:
                email = EmailMultiAlternatives(
                    subject=subject,
                    body=text_body,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[tx.student.email],
                )
                email.attach_alternative(html_body, 'text/html')
                email.send(fail_silently=False)
                sent_count += 1
            except Exception as e:
                logger.error("Failed to send manual email to %s: %s", tx.student.email, e)

        if sent_count > 0:
            messages.success(request, f"Successfully sent {sent_count} reminder(s) to {student.name} ({student.email}).")
        else:
            messages.error(request, "Failed to send email reminders. Check server logs.")

        return redirect('admin_manual_reminder')

    return render(request, 'admin/manual_reminder.html', context)


@require_GET
def book_search(request):
    """Public search page for books by ISBN or Title."""
    query = request.GET.get('q', '').strip()
    
    books = Book.objects.all()
    if query:
        books = books.filter(Q(title__icontains=query) | Q(isbn_no__icontains=query))
        
    total_books = books.count()
    available_books = books.filter(status='Available').count()
    
    context = {
        'query': query,
        'books': books,
        'total_books': total_books,
        'available_books': available_books,
    }
    return render(request, 'management/search.html', context)
