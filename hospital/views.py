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