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
                messages.success(request, f"zk Welcome, {student.name}! Access Granted.")
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
    return render(request, 'management/dashboard.html', {'live_logs': live_logs})
