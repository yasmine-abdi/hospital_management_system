from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages  # <--- Kani wuxuu xallinayaa messages-ka maqnaa!

# Moodalada waxaa laga soo jiidayaa .models
from .models import Patient, Doctor, Appointment 

# Foomamka waxaa laga soo jiidayaa .forms
from .forms import PatientForm, DoctorForm, AppointmentForm 


# ==========================================
# AUTHENTICATION VIEWS
# ==========================================
def login_view(request):
    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        user = authenticate(request, username=u, password=p)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'login.html', {'error': 'Username ama Password qaldan'})
    return render(request, 'login.html')


def dashboard_view(request):
    return render(request, 'dashboard.html')


# ==========================================
# PATIENT MANAGEMENT VIEWS
# ==========================================
@login_required
def add_patient_view(request):
    doctors = Doctor.objects.all()
    if request.method == 'POST':
        form = PatientForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Bukaanka si guul ah ayaa loo diiwangeliyey!')
            return redirect('patient_list')
    else:
        form = PatientForm()
    return render(request, 'add_patient.html', {'form': form, 'doctors': doctors})


@login_required
def patient_list_view(request):
    from django.utils import timezone
    today = timezone.now().date()
    
    # Hadda Patient wuxuu si toos ah u akhrinayaa Model-ka rasmiga ah
    patients = Patient.objects.all().order_by('-created_at')
    
    total_patients = patients.count()
    male_patients = patients.filter(gender='Male').count()
    female_patients = patients.filter(gender='Female').count()
    new_patients_today = patients.filter(created_at__date=today).count()
    
    context = {
        'patients': patients,
        'total_patients': total_patients,
        'male_patients': male_patients,
        'female_patients': female_patients,
        'new_patients_today': new_patients_today,
    }
    return render(request, 'patient_list.html', context)


# ==========================================
# DOCTOR MANAGEMENT VIEWS
# ==========================================
# 1. Liiska Dhakhaatiirta dhan
def doctor_list(request):
    from .models import Specialization
    doctors = Doctor.objects.all().select_related('user', 'specialization')
    
    total_doctors = doctors.count()
    available_doctors = doctors.filter(is_available=True).count()
    unavailable_doctors = doctors.filter(is_available=False).count()
    total_specializations = Specialization.objects.count()

    context = {
        'doctors': doctors,
        'total_doctors': total_doctors,
        'available_doctors': available_doctors,
        'unavailable_doctors': unavailable_doctors,
        'total_specializations': total_specializations,
    }
    return render(request, 'hospital/doctor_list.html', context)


# 2. Xogta gaarka ah ee Dhakhtarka
def doctor_detail(request, pk):
    doctor = get_object_or_404(Doctor, pk=pk)
    assigned_patients = Patient.objects.filter(doctor=doctor)
    appointments = Appointment.objects.filter(doctor=doctor).order_by('-appointment_date')
    
    context = {
        'doctor': doctor,
        'assigned_patients': assigned_patients,
        'appointments': appointments
    }
    return render(request, 'hospital/doctor_detail.html', context)


# 3. Diiwangelinta Dhakhtar Cusub
def doctor_create(request):
    if request.method == 'POST':
        form = DoctorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Dhakhtarka waa la diiwaangeliyay si guul ah!')
            return redirect('doctor_list')
    else:
        form = DoctorForm()
    return render(request, 'hospital/doctor_form.html', {'form': form, 'title': 'Diiwaangeli Dhakhtar Cusub'})


# 4. Wax ka beddelka Xogta Dhakhtarka
def doctor_update(request, pk):
    doctor = get_object_or_404(Doctor, pk=pk)
    if request.method == 'POST':
        form = DoctorForm(request.POST, instance=doctor)
        if form.is_valid():
            form.save()
            messages.success(request, 'Xogta dhakhtarka waa la cusboonaysiiyay!')
            return redirect('doctor_list')
    else:
        form = DoctorForm(instance=doctor)
    return render(request, 'hospital/doctor_form.html', {'form': form, 'title': 'Wax ka beddel Xogta Dhakhtarka'})


# 5. Tiridda Dhakhtarka
def doctor_delete(request, pk):
    doctor = get_object_or_404(Doctor, pk=pk)
    if request.method == 'POST':
        doctor.delete()
        messages.warning(request, 'Dhakhtarka waa laga saaray system-ka!')
        return redirect('doctor_list')
    return render(request, 'hospital/doctor_confirm_delete.html', {'doctor': doctor})


# ==========================================
# APPOINTMENT MANAGEMENT VIEWS
# ==========================================
def appointment_list(request):
    appointments = Appointment.objects.all().select_related('patient', 'doctor', 'doctor__user', 'doctor__specialization').order_by('-appointment_date')
    
    total_appointments = appointments.count()
    pending_appointments = appointments.filter(status='Pending').count()
    approved_appointments = appointments.filter(status='Approved').count()
    completed_appointments = appointments.filter(status='Completed').count()

    context = {
        'appointments': appointments,
        'total_appointments': total_appointments,
        'pending_appointments': pending_appointments,
        'approved_appointments': approved_appointments,
        'completed_appointments': completed_appointments,
    }
    return render(request, 'hospital/appointment_list.html', context)

def appointment_create(request):
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ballanta waa la qabtay si guul ah!')
            return redirect('appointment_list')
    else:
        form = AppointmentForm()
    return render(request, 'hospital/appointment_form.html', {'form': form, 'title': 'Qabo Ballan Cusub'})

def appointment_update(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    if request.method == 'POST':
        form = AppointmentForm(request.POST, instance=appointment)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ballanta waa la cusboonaysiiyay si guul ah!')
            return redirect('appointment_list')
    else:
        form = AppointmentForm(instance=appointment)
    return render(request, 'hospital/appointment_form.html', {'form': form, 'title': 'Beddel Xogta Ballanta'})

def appointment_delete(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    if request.method == 'POST':
        appointment.delete()
        messages.success(request, 'Ballanta waa la tiray!')
        return redirect('appointment_list')
    return render(request, 'hospital/appointment_confirm_delete.html', {'appointment': appointment})

# ==========================================
# PHARMACY MANAGEMENT VIEWS
# ==========================================
from .models import Medicine, PharmacySale, PharmacySaleItem
from .forms import MedicineForm, PharmacySaleForm
from django.forms import inlineformset_factory

@login_required
def medicine_list(request):
    medicines = Medicine.objects.all().order_by('name')
    
    total_medicines = medicines.count()
    in_stock = medicines.filter(stock_quantity__gt=0).count()
    out_of_stock = medicines.filter(stock_quantity=0).count()
    low_stock = medicines.filter(stock_quantity__gt=0, stock_quantity__lte=10).count()

    context = {
        'medicines': medicines,
        'total_medicines': total_medicines,
        'in_stock': in_stock,
        'out_of_stock': out_of_stock,
        'low_stock': low_stock,
    }
    return render(request, 'pharmacy/medicine_list.html', context)

@login_required
def medicine_create(request):
    if request.method == 'POST':
        form = MedicineForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Daawada waa la diiwaangeliyay!')
            return redirect('medicine_list')
    else:
        form = MedicineForm()
    return render(request, 'pharmacy/medicine_form.html', {'form': form, 'title': 'Diiwaangeli Daawo Cusub'})

@login_required
def medicine_update(request, pk):
    medicine = get_object_or_404(Medicine, pk=pk)
    if request.method == 'POST':
        form = MedicineForm(request.POST, instance=medicine)
        if form.is_valid():
            form.save()
            messages.success(request, 'Xogta daawada waa la cusboonaysiiyay!')
            return redirect('medicine_list')
    else:
        form = MedicineForm(instance=medicine)
    return render(request, 'pharmacy/medicine_form.html', {'form': form, 'title': 'Beddel Xogta Daawada'})

@login_required
def medicine_delete(request, pk):
    medicine = get_object_or_404(Medicine, pk=pk)
    if request.method == 'POST':
        medicine.delete()
        messages.warning(request, 'Daawada waa la tiray!')
        return redirect('medicine_list')
    return render(request, 'pharmacy/medicine_confirm_delete.html', {'medicine': medicine})

@login_required
def pharmacy_sale_list(request):
    from django.utils import timezone
    from django.db.models import Sum, Q
    from datetime import datetime

    today = timezone.now().date()
    sales = PharmacySale.objects.all().order_by('-sale_date')

    # Filtering logic
    selected_month = request.GET.get('month')
    selected_year = request.GET.get('year')
    search_query = request.GET.get('q')
    
    if selected_month and selected_year:
        sales = sales.filter(sale_date__year=selected_year, sale_date__month=selected_month)
        
    if search_query:
        sales = sales.filter(
            Q(invoice_number__icontains=search_query) | 
            Q(patient__name__icontains=search_query) |
            Q(id__icontains=search_query)
        )
    
    total_sales = sales.count()
    sales_today = sales.filter(sale_date__date=today).count() if not (selected_month and selected_year or search_query) else 0
    revenue_today = sales.filter(sale_date__date=today).aggregate(Sum('total_amount'))['total_amount__sum'] or 0 if not (selected_month and selected_year or search_query) else 0
    total_revenue = sales.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    
    context = {
        'sales': sales,
        'total_sales': total_sales,
        'sales_today': sales_today,
        'revenue_today': revenue_today,
        'total_revenue': total_revenue,
        'selected_month': int(selected_month) if selected_month else today.month,
        'selected_year': int(selected_year) if selected_year else today.year,
        'months': range(1, 13),
        'years': range(today.year - 5, today.year + 2),
    }
    return render(request, 'pharmacy/sale_list.html', context)

@login_required
def pharmacy_sale_create(request):
    PharmacySaleItemFormSet = inlineformset_factory(
        PharmacySale, PharmacySaleItem, fields=('medicine', 'quantity', 'unit_price'), extra=3, can_delete=True
    )
    if request.method == 'POST':
        form = PharmacySaleForm(request.POST)
        formset = PharmacySaleItemFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            sale = form.save()
            instances = formset.save(commit=False)
            total = 0
            for instance in instances:
                instance.sale = sale
                med = instance.medicine
                med.stock_quantity -= instance.quantity
                med.save()
                instance.total = instance.quantity * instance.unit_price
                total += instance.total
                instance.save()
            
            sale.total_amount = total
            sale.save()
            
            messages.success(request, 'Iibka daawada si guul ah ayuu ku dhacay!')
            return redirect('pharmacy_sale_detail', pk=sale.pk)
    else:
        form = PharmacySaleForm()
        formset = PharmacySaleItemFormSet()
    
    return render(request, 'pharmacy/sale_form.html', {'form': form, 'formset': formset})

@login_required
def pharmacy_sale_detail(request, pk):
    sale = get_object_or_404(PharmacySale, pk=pk)
    return render(request, 'pharmacy/sale_detail.html', {'sale': sale})

# ==========================================
# INPATIENT (IPD) MANAGEMENT VIEWS
# ==========================================
from .models import Ward, Bed, Admission
from .forms import WardForm, BedForm, AdmissionForm
from django.utils import timezone

@login_required
def admission_list(request):
    admissions = Admission.objects.all().order_by('-admission_date')
    
    total_admitted = admissions.filter(status='Admitted').count()
    total_discharged = admissions.filter(status='Discharged').count()
    total_wards = Ward.objects.count()
    available_beds = Bed.objects.filter(is_available=True).count()
    
    context = {
        'admissions': admissions,
        'total_admitted': total_admitted,
        'total_discharged': total_discharged,
        'total_wards': total_wards,
        'available_beds': available_beds
    }
    return render(request, 'inpatient/admission_list.html', context)

@login_required
def admission_create(request):
    if request.method == 'POST':
        form = AdmissionForm(request.POST)
        if form.is_valid():
            admission = form.save()
            # Mark the bed as unavailable
            bed = admission.bed
            bed.is_available = False
            bed.save()
            messages.success(request, 'Bukaanka si guul ah ayaa loo seexiyay (Admitted).')
            return redirect('admission_list')
    else:
        form = AdmissionForm()
    return render(request, 'inpatient/admission_form.html', {'form': form, 'title': 'Diiwaangeli Bukaan-jiif Cusub'})

@login_required
def admission_update(request, pk):
    admission = get_object_or_404(Admission, pk=pk)
    old_bed = admission.bed
    if request.method == 'POST':
        form = AdmissionForm(request.POST, instance=admission)
        if form.is_valid():
            new_admission = form.save()
            # Update beds if changed
            if 'bed' in form.changed_data:
                old_bed.is_available = True
                old_bed.save()
                new_bed = new_admission.bed
                new_bed.is_available = False
                new_bed.save()
                
            messages.success(request, 'Xogta bukaan-jiifka waa la cusboonaysiiyay.')
            return redirect('admission_list')
    else:
        form = AdmissionForm(instance=admission)
    return render(request, 'inpatient/admission_form.html', {'form': form, 'title': 'Beddel Xogta Bukaan-jiifka'})

@login_required
def discharge_patient(request, pk):
    admission = get_object_or_404(Admission, pk=pk)
    if request.method == 'POST':
        admission.status = 'Discharged'
        admission.discharge_date = timezone.now()
        admission.save()
        
        # Free up the bed
        bed = admission.bed
        bed.is_available = True
        bed.save()
        
        messages.success(request, f'Bukaanka {admission.patient.name} si guul ah ayaa loo fasaxay (Discharged).')
        return redirect('admission_list')
    return render(request, 'inpatient/admission_confirm_discharge.html', {'admission': admission})

@login_required
def bed_list(request):
    wards = Ward.objects.prefetch_related('bed_set').all()
    total_beds = Bed.objects.count()
    available_beds = Bed.objects.filter(is_available=True).count()
    occupied_beds = total_beds - available_beds
    
    context = {
        'wards': wards,
        'total_beds': total_beds,
        'available_beds': available_beds,
        'occupied_beds': occupied_beds
    }
    return render(request, 'inpatient/bed_list.html', context)

@login_required
def bed_create(request):
    if request.method == 'POST':
        form = BedForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Sariir cusub si guul ah ayaa loo diiwaangeliyay!')
            return redirect('bed_list')
    else:
        form = BedForm()
    return render(request, 'inpatient/bed_form.html', {'form': form, 'title': 'Diiwaangeli Sariir Cusub'})

@login_required
def ward_create(request):
    if request.method == 'POST':
        form = WardForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Qeyb (Ward) cusub ayaa la abuuray!')
            return redirect('bed_list') # AMA bed_create haddii loo baahdo
    else:
        form = WardForm()
    return render(request, 'inpatient/ward_form.html', {'form': form, 'title': 'Abuur Qeyb (Ward) Cusub'})