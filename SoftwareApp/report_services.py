import io
from datetime import datetime, time
from django.utils import timezone
from django.db.models import Count, Q
from AdminApp.models import CRMFollowup, Branch, CustomUser

# ReportLab imports for PDF generation
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether
from reportlab.pdfgen import canvas

# openpyxl imports for Excel generation
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter


# ==========================================
# 1. ROLE-BASED ACCESS CONTROL (RBAC) SCOPING
# ==========================================

def scope_crm_queryset(user, queryset=None):
    """
    Strictly enforce Role-Based Row-Level Security:
    - Superuser: Global access.
    - CRM Manager / CRM & Enrollment: Scoped to their assigned branch.
    - Salesperson / Telecaller / Counselor / Staff: Strictly scoped to their own assigned leads (follow_up_by=user).
    """
    if queryset is None:
        queryset = CRMFollowup.objects.all()

    if user.is_superuser:
        return queryset

    user_role = getattr(user, 'role', None)

    # CRM Managers & Branch Managers see branch leads
    if user_role in ['is_crm_manager', 'is_crm_and_enrollment']:
        # If user has an associated branch attribute or profile
        user_branch = getattr(user, 'branch', None)
        if user_branch:
            return queryset.filter(branch=user_branch)
        return queryset

    # Regular salespersons / telecallers / staff strictly see only their assigned leads
    return queryset.filter(follow_up_by=user)


# ==========================================
# 2. REPORT DATA COMPUTATION SERVICES
# ==========================================

def get_calling_agenda_data(user, target_date=None):
    """
    Computes daily calling task sheet for the salesperson / counselor:
    - Today's Scheduled Calls: Reminders set for target_date.
    - Overdue Calls: Reminders set before target_date not yet converted or closed.
    """
    if target_date is None:
        target_date = timezone.now().date()
    elif isinstance(target_date, str):
        target_date = datetime.strptime(target_date, '%Y-%m-%d').date()

    start_of_day = timezone.make_aware(datetime.combine(target_date, time.min))
    end_of_day = timezone.make_aware(datetime.combine(target_date, time.max))

    qs = scope_crm_queryset(user).select_related('student_interested_for', 'branch', 'follow_up_by')

    # Today's scheduled calls
    today_qs = qs.filter(
        next_followup_reminder__range=(start_of_day, end_of_day)
    ).order_by('next_followup_reminder')

    # Overdue pending calls (scheduled before today, not joined or not interested)
    overdue_qs = qs.filter(
        next_followup_reminder__lt=start_of_day
    ).exclude(
        status__in=['class_joined', 'class_completed', 'not_interested']
    ).order_by('next_followup_reminder')

    def serialize_lead(item, is_overdue=False):
        priority_val = item.priority or 'medium'
        status_val = item.status or 'interested'
        prio_disp = item.get_priority_display() if hasattr(item, 'get_priority_display') else priority_val
        status_disp = item.get_status_display() if hasattr(item, 'get_status_display') else status_val

        return {
            'id': item.id,
            'name': item.name or 'Unknown',
            'mobile_number': item.mobile_number or '—',
            'interested_course': item.student_interested_for.interest_option if item.student_interested_for else 'General Inquiry',
            'status': status_val,
            'status_display': status_disp or status_val.capitalize(),
            'priority': priority_val,
            'priority_display': prio_disp or priority_val.capitalize(),
            'branch': item.branch.branch_name if item.branch else 'Unassigned',
            'reminder_time': item.next_followup_reminder.strftime('%I:%M %p') if item.next_followup_reminder else 'No Time',
            'reminder_date': item.next_followup_reminder.strftime('%Y-%m-%d') if item.next_followup_reminder else '',
            'last_notes': item.follow_up_notes or '',
            'is_overdue': is_overdue,
        }

    today_leads = [serialize_lead(l, False) for l in today_qs]
    overdue_leads = [serialize_lead(l, True) for l in overdue_qs]

    return {
        'target_date': target_date.strftime('%Y-%m-%d'),
        'counselor_name': user.name if hasattr(user, 'name') and user.name else user.username,
        'summary': {
            'today_count': len(today_leads),
            'overdue_count': len(overdue_leads),
            'total_agenda_count': len(today_leads) + len(overdue_leads),
            'high_priority_count': sum(1 for l in (today_leads + overdue_leads) if l['priority'] == 'high'),
        },
        'today_calls': today_leads,
        'overdue_calls': overdue_leads,
    }


def get_counselor_performance_data(user, date_from=None, date_to=None):
    """
    Computes personal conversion and pipeline performance KPIs for the logged-in counselor.
    """
    qs = scope_crm_queryset(user)

    if date_from:
        if isinstance(date_from, str):
            date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
        qs = qs.filter(created_at__date__gte=date_from)

    if date_to:
        if isinstance(date_to, str):
            date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
        qs = qs.filter(created_at__date__lte=date_to)

    total_assigned = qs.count()
    joined_count = qs.filter(status__in=['class_joined', 'class_completed']).count()
    interested_count = qs.filter(status='interested').count()
    planning_count = qs.filter(status='planning').count()
    under_review_count = qs.filter(status='under_review').count()
    on_hold_count = qs.filter(status='on_hold').count()
    not_interested_count = qs.filter(status='not_interested').count()

    conversion_rate = round((joined_count / total_assigned * 100), 1) if total_assigned > 0 else 0.0

    # Overdue count
    now = timezone.now()
    overdue_count = qs.filter(
        next_followup_reminder__lt=now
    ).exclude(
        status__in=['class_joined', 'class_completed', 'not_interested']
    ).count()

    return {
        'counselor_name': user.name if hasattr(user, 'name') and user.name else user.username,
        'date_from': str(date_from) if date_from else 'All Time',
        'date_to': str(date_to) if date_to else 'Today',
        'metrics': {
            'total_assigned': total_assigned,
            'class_joined': joined_count,
            'conversion_rate_percent': conversion_rate,
            'active_in_pipeline': interested_count + planning_count + under_review_count,
            'on_hold': on_hold_count,
            'not_interested': not_interested_count,
            'overdue_reminders': overdue_count,
        },
        'status_breakdown': [
            {'label': 'Class Joined / Enrolled', 'status': 'class_joined', 'count': joined_count, 'color': '#10B981'},
            {'label': 'Interested', 'status': 'interested', 'count': interested_count, 'color': '#0EA5E9'},
            {'label': 'Planning', 'status': 'planning', 'count': planning_count, 'color': '#6366F1'},
            {'label': 'Under Review', 'status': 'under_review', 'count': under_review_count, 'color': '#F59E0B'},
            {'label': 'On Hold', 'status': 'on_hold', 'count': on_hold_count, 'color': '#64748B'},
            {'label': 'Not Interested', 'status': 'not_interested', 'count': not_interested_count, 'color': '#E11D48'},
        ],
    }


def get_branch_funnel_data(user, branch_id=None, date_from=None, date_to=None):
    """
    Computes branch-level pipeline funnel and counselor performance comparison.
    Accessible only by CRM Managers, Branch Managers, and Super Admins.
    """
    qs = CRMFollowup.objects.all()

    if not user.is_superuser:
        user_role = getattr(user, 'role', None)
        if user_role not in ['is_crm_manager', 'is_crm_and_enrollment']:
            raise PermissionError("Access restricted to CRM Managers and Directors.")
        user_branch = getattr(user, 'branch', None)
        if user_branch:
            qs = qs.filter(branch=user_branch)
            branch_id = user_branch.id
    elif branch_id:
        qs = qs.filter(branch_id=branch_id)

    if date_from:
        if isinstance(date_from, str):
            date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
        qs = qs.filter(created_at__date__gte=date_from)

    if date_to:
        if isinstance(date_to, str):
            date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
        qs = qs.filter(created_at__date__lte=date_to)

    total_branch_leads = qs.count()
    joined_total = qs.filter(status__in=['class_joined', 'class_completed']).count()
    branch_conversion_rate = round((joined_total / total_branch_leads * 100), 1) if total_branch_leads > 0 else 0.0

    # Team Counselor Breakdown
    counselor_stats = (
        qs.values('follow_up_by__id', 'follow_up_by__name')
        .annotate(
            total_leads=Count('id'),
            joined_leads=Count('id', filter=Q(status__in=['class_joined', 'class_completed'])),
            overdue_leads=Count('id', filter=Q(next_followup_reminder__lt=timezone.now()) & ~Q(status__in=['class_joined', 'class_completed', 'not_interested'])),
        )
        .order_by('-total_leads')
    )

    counselors_list = []
    for c in counselor_stats:
        t = c['total_leads']
        j = c['joined_leads']
        rate = round((j / t * 100), 1) if t > 0 else 0.0
        counselors_list.append({
            'counselor_id': c['follow_up_by__id'],
            'counselor_name': c['follow_up_by__name'] or 'Unassigned',
            'total_leads': t,
            'joined_leads': j,
            'overdue_leads': c['overdue_leads'],
            'conversion_rate_percent': rate,
        })

    # Lead Source Effectiveness (ROI)
    source_stats = (
        qs.values('source')
        .annotate(
            total=Count('id'),
            joined=Count('id', filter=Q(status__in=['class_joined', 'class_completed'])),
        )
        .order_by('-total')
    )

    source_list = []
    for s in source_stats:
        t = s['total']
        j = s['joined']
        rate = round((j / t * 100), 1) if t > 0 else 0.0
        source_list.append({
            'source': s['source'] or 'unknown',
            'source_display': (s['source'] or 'Unknown').capitalize(),
            'total_leads': t,
            'joined_leads': j,
            'conversion_rate_percent': rate,
        })

    branch_name = 'All Branches'
    if branch_id:
        try:
            branch_obj = Branch.objects.get(id=branch_id)
            branch_name = branch_obj.branch_name
        except Branch.DoesNotExist:
            pass

    return {
        'branch_name': branch_name,
        'date_from': str(date_from) if date_from else 'All Time',
        'date_to': str(date_to) if date_to else 'Today',
        'summary': {
            'total_leads': total_branch_leads,
            'joined_leads': joined_total,
            'conversion_rate_percent': branch_conversion_rate,
        },
        'counselor_performance': counselors_list,
        'source_effectiveness': source_list,
    }


# ==========================================
# 3. PDF EXPORT GENERATOR (WITH SECURITY WATERMARK)
# ==========================================

class NumberedCanvas(canvas.Canvas):
    """Adds page numbers and security watermark to every page."""
    def __init__(self, *args, **kwargs):
        self.watermark_text = kwargs.pop('watermark_text', 'Confidential - VR Academy Hub CRM')
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))

        # Footer security watermark
        self.drawString(36, 20, self.watermark_text)
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(A4[0] - 36, 20, page_text)
        self.restoreState()


def generate_agenda_pdf(user, agenda_data, target_date=None):
    """
    Renders a clean, professional, printable PDF for the daily calling agenda.
    Includes security footer with generator name, timestamp, and role.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=40,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#1E1B4B'),
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#475569'),
    )
    section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#312E81'),
        spaceBefore=10,
        spaceAfter=6,
    )
    cell_style = ParagraphStyle(
        'CellText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor('#0F172A'),
    )
    cell_bold = ParagraphStyle(
        'CellBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor('#0F172A'),
    )
    cell_badge_high = ParagraphStyle(
        'CellHigh',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor('#BE123C'),
    )

    story = []

    # Title & Header
    counselor = agenda_data.get('counselor_name', 'Salesperson')
    date_str = agenda_data.get('target_date', str(timezone.now().date()))
    story.append(Paragraph("VR ACADEMY HUB • CRM ACTION SHEET", title_style))
    story.append(Paragraph(f"Daily Calling & Follow-up Agenda • <b>Date:</b> {date_str} • <b>Counselor:</b> {counselor}", subtitle_style))
    story.append(Spacer(1, 10))

    # Metric KPI Summary Row
    summary = agenda_data.get('summary', {})
    kpi_data = [[
        f"Today's Scheduled: {summary.get('today_count', 0)}",
        f"Overdue Calls: {summary.get('overdue_count', 0)}",
        f"Total Agenda: {summary.get('total_agenda_count', 0)}",
        f"High Priority: {summary.get('high_priority_count', 0)}",
    ]]
    kpi_table = Table(kpi_data, colWidths=[130, 130, 130, 130])
    kpi_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#EEF2FF')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#3730A3')),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('INNERGRID', (0, 0), (-1, -1), 1, colors.HexColor('#C7D2FE')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#818CF8')),
    ]))
    story.append(kpi_table)
    story.append(Spacer(1, 14))

    from xml.sax.saxutils import escape

    def build_leads_table(leads, is_overdue_table=False):
        table_rows = [[
            Paragraph("<b>#</b>", cell_bold),
            Paragraph("<b>Student Name</b>", cell_bold),
            Paragraph("<b>Mobile</b>", cell_bold),
            Paragraph("<b>Interested Course</b>", cell_bold),
            Paragraph("<b>Priority</b>", cell_bold),
            Paragraph("<b>Time / Status</b>", cell_bold),
            Paragraph("<b>Notes / Discussion</b>", cell_bold),
        ]]

        for i, lead in enumerate(leads, start=1):
            prio_style = cell_badge_high if lead['priority'] == 'high' else cell_style
            name_esc = escape(str(lead.get('name') or ''))
            mobile_esc = escape(str(lead.get('mobile_number') or ''))
            course_esc = escape(str(lead.get('interested_course') or ''))
            prio_esc = escape(str(lead.get('priority_display') or ''))
            time_esc = escape(str(lead.get('reminder_time') or ''))
            status_esc = escape(str(lead.get('status_display') or ''))
            notes_esc = escape(str((lead.get('last_notes') or '')[:120])) or '—'

            time_status = f"{time_esc}<br/>({status_esc})"
            table_rows.append([
                Paragraph(str(i), cell_style),
                Paragraph(f"<b>{name_esc}</b>", cell_style),
                Paragraph(mobile_esc, cell_style),
                Paragraph(course_esc, cell_style),
                Paragraph(prio_esc, prio_style),
                Paragraph(time_status, cell_style),
                Paragraph(notes_esc, cell_style),
            ])

        t = Table(table_rows, colWidths=[24, 95, 75, 95, 65, 80, 88])
        header_bg = colors.HexColor('#FFE4E6') if is_overdue_table else colors.HexColor('#F1F5F9')
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), header_bg),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ]))
        return t

    # Today's Scheduled Section
    today_calls = agenda_data.get('today_calls', [])
    story.append(Paragraph(f"📅 Today's Scheduled Calls ({len(today_calls)})", section_heading))
    if today_calls:
        story.append(build_leads_table(today_calls, is_overdue_table=False))
    else:
        story.append(Paragraph("<i>No follow-ups scheduled for today.</i>", subtitle_style))

    # Overdue Section
    overdue_calls = agenda_data.get('overdue_calls', [])
    if overdue_calls:
        story.append(Spacer(1, 14))
        story.append(Paragraph(f"⚠️ Overdue Calls Requiring Immediate Action ({len(overdue_calls)})", section_heading))
        story.append(build_leads_table(overdue_calls, is_overdue_table=True))

    timestamp_str = timezone.now().strftime('%d-%b-%Y %I:%M %p')
    watermark = f"CONFIDENTIAL • Generated by {counselor} on {timestamp_str} • Internal Use Only"

    def canvas_maker(*args, **kwargs):
        return NumberedCanvas(*args, watermark_text=watermark, **kwargs)

    doc.build(story, canvasmaker=canvas_maker)
    buffer.seek(0)
    return buffer.getvalue()


# ==========================================
# 4. EXCEL EXPORT GENERATOR (WITH STYLING)
# ==========================================

def generate_agenda_excel(user, agenda_data):
    """
    Generates a formatted Excel spreadsheet for daily calling tasks.
    """
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Daily Agenda"

    # Styling definitions
    header_fill = PatternFill(start_color="312E81", end_color="312E81", fill_type="solid")
    overdue_fill = PatternFill(start_color="991B1B", end_color="991B1B", fill_type="solid")
    kpi_fill = PatternFill(start_color="EEF2FF", end_color="EEF2FF", fill_type="solid")
    zebra_fill = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")

    font_title = Font(name="Calibri", size=14, bold=True, color="1E1B4B")
    font_sub = Font(name="Calibri", size=10, italic=True, color="475569")
    font_header = Font(name="Calibri", size=10, bold=True, color="FFFFFF")
    font_kpi = Font(name="Calibri", size=10, bold=True, color="3730A3")
    font_cell = Font(name="Calibri", size=10, color="0F172A")
    font_watermark = Font(name="Calibri", size=8, italic=True, color="94A3B8")

    thin_border = Border(
        left=Side(style='thin', color='CBD5E1'),
        right=Side(style='thin', color='CBD5E1'),
        top=Side(style='thin', color='CBD5E1'),
        bottom=Side(style='thin', color='CBD5E1')
    )

    counselor = agenda_data.get('counselor_name', 'Counselor')
    date_str = agenda_data.get('target_date', '')

    # Title & Metadata
    ws['A1'] = "VR ACADEMY HUB • CRM DAILY CALLING TASK SHEET"
    ws['A1'].font = font_title
    ws['A2'] = f"Counselor: {counselor} | Date: {date_str} | Generated: {timezone.now().strftime('%Y-%m-%d %H:%M')}"
    ws['A2'].font = font_sub

    # Table Header Row
    headers = ["#", "Student Name", "Mobile Number", "Interested Course", "Priority", "Status", "Reminder Time", "Branch", "Follow-up Notes"]
    row_idx = 4
    for col_idx, header in enumerate(headers, start=1):
        cell = ws.cell(row=row_idx, column=col_idx, value=header)
        cell.font = font_header
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = thin_border

    all_leads = []
    for l in agenda_data.get('today_calls', []):
        l['_type'] = 'Today'
        all_leads.append(l)
    for l in agenda_data.get('overdue_calls', []):
        l['_type'] = 'Overdue'
        all_leads.append(l)

    row_idx = 5
    for i, lead in enumerate(all_leads, start=1):
        row_data = [
            i,
            lead['name'],
            lead['mobile_number'],
            lead['interested_course'],
            lead['priority_display'],
            f"{lead['status_display']} ({lead['_type']})",
            lead['reminder_time'],
            lead['branch'],
            lead['last_notes']
        ]

        for col_idx, val in enumerate(row_data, start=1):
            cell = ws.cell(row=row_idx, column=col_idx, value=val)
            cell.font = font_cell
            cell.border = thin_border
            if lead['_type'] == 'Overdue':
                cell.fill = PatternFill(start_color="FFF1F2", end_color="FFF1F2", fill_type="solid")
            elif row_idx % 2 == 0:
                cell.fill = zebra_fill
            cell.alignment = Alignment(vertical="center", wrap_text=(col_idx == 9))

        row_idx += 1

    # Security Watermark Footer
    row_idx += 1
    ws.cell(row=row_idx, column=1, value=f"CONFIDENTIAL • Scoped to {counselor} • VR Academy Hub CRM Security System").font = font_watermark

    # Auto-adjust column widths
    for col in ws.columns:
        max_len = max(len(str(cell.value or '')) for cell in col)
        col_letter = get_column_letter(col[0].column)
        ws.column_dimensions[col_letter].width = min(max(max_len + 3, 12), 40)

    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer.getvalue()
