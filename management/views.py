import logging
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_http_methods, require_GET
from .models import Student, LibraryLog
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
                messages.success(request, f"👋 Goodbye, {student.name}! See you next time.")
                logger.info("Student %s checked OUT", student.enrollment_id)
            else:
                LibraryLog.objects.create(student=student)
                messages.success(request, f"Welcome, {student.name}! Access Granted.")
                logger.info("Student %s checked IN", student.enrollment_id)
                
        except Student.DoesNotExist:
            messages.error(request, f"🚫 Access Denied: Student ID '{barcode}' not found or not registered.")
            logger.warning("Unknown barcode scanned: %s", barcode)

        return redirect('kiosk')

    return render(request, 'management/kiosk.html')


@staff_member_required(login_url='/admin/login/')
@require_GET
def dashboard(request):
    """Admin-only dashboard showing who is currently in the library."""
    live_logs = (
        LibraryLog.objects
        .filter(exit_time__isnull=True)
        .select_related('student')
        .order_by('-entry_time')
    )
    total_visits = LibraryLog.objects.count()
    context = {
        'live_logs': live_logs,
        'total_visits': total_visits,
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

