from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.contrib.auth.models import User # Si aan u isticmaalno Doctor-ka


# ==========================================
# 1. ACCOUNT AND AUTHENTICATION
# ==========================================
class User(AbstractUser):
    ROLE_CHOICES = [
        ('Admin', 'Admin'), 
        ('Doctor', 'Doctor'), 
        ('Nurse', 'Nurse'),
        ('Pharmacist', 'Pharmacist'), 
        ('Receptionist', 'Receptionist'),
        ('Lab Technician', 'Lab Technician'),
    ]
    role = models.CharField(max_length=50, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.username} ({self.role})"

# ==========================================
# 2. PROFILES (Doctor, Nurse, Receptionist)
# ==========================================


class Nurse(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='nurse_profile')
    qualification = models.CharField(max_length=100)
    phone = models.CharField(max_length=50)

    def __str__(self): return f"Nurse {self.user.username}"

class Receptionist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='receptionist_profile')
    shift = models.CharField(max_length=50)
    phone = models.CharField(max_length=50)

    def __str__(self): return f"Receptionist {self.user.username}"

# ==========================================
# 3. RECEPTION & PATIENT MANAGEMENT
# ==========================================
class Patient(models.Model):
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female')])
    address = models.TextField()
    phone = models.CharField(max_length=15)
    doctor = models.ForeignKey('Doctor', on_delete=models.SET_NULL, null=True, related_name='patients')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
    
    # ==========================================
# 3. DOCTOR MANAGEMENT (Sida uu PDF-ka ku qoran yahay)
# ==========================================
class Specialization(models.Model):
    name = models.CharField(max_length=100, unique=True) # Tusaale: Cardiology, Pediatrics

    def __str__(self):
        return self.name

class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='doctor_profile')
    specialization = models.ForeignKey(Specialization, on_delete=models.SET_NULL, null=True, related_name='doctors')
    phone = models.CharField(max_length=50)
    shift_start = models.TimeField(null=True, blank=True) # Waqtiga uu shaqada bilaabo
    shift_end = models.TimeField(null=True, blank=True)   # Waqtiga uu shaqada dhameeyo
    is_available = models.BooleanField(default=True)      # Hubinta inuu dhakhtarku joogo

    def __str__(self): 
        return f"Dr. {self.user.first_name} {self.user.last_name} ({self.specialization.name if self.specialization else 'N/A'})"
# ==========================================
# 4. STAFF MANAGEMENT (General)
# ==========================================
class Staff(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='staff_profile')
    department = models.CharField(max_length=100)
    hire_date = models.DateField(default=timezone.now)

# ==========================================
# 5. APPOINTMENT MANAGEMENT
# ==========================================
class Appointment(models.Model):
    STATUS = [('Pending', 'Pending'), ('Approved', 'Approved'), ('Completed', 'Completed')]
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    appointment_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS, default='Pending')

# ==========================================
# 6. PHARMACY MANAGEMENT
# ==========================================
class Medicine(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True, null=True)
    batch_number = models.CharField(max_length=50, blank=True, null=True)
    expiry_date = models.DateField(blank=True, null=True)
    stock_quantity = models.IntegerField(default=0)
    unit_price = models.DecimalField(max_digits=18, decimal_places=2)

    def __str__(self):
        return self.name

    @property
    def is_in_stock(self):
        return self.stock_quantity > 0

class PharmacySale(models.Model):
    invoice_number = models.CharField(max_length=50, unique=True, blank=True, null=True)
    patient = models.ForeignKey(Patient, on_delete=models.SET_NULL, null=True, related_name='pharmacy_sales')
    total_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0.0)
    sale_date = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new and not self.invoice_number:
            self.invoice_number = f"INV-{self.pk:03d}"
            kwargs['force_insert'] = False
            super().save(*args, **kwargs)

    def __str__(self):
        patient_name = self.patient.name if self.patient else "Walk-in"
        inv = self.invoice_number if self.invoice_number else f"Sale #{self.id}"
        return f"{inv} - {patient_name}"

class PharmacySaleItem(models.Model):
    sale = models.ForeignKey(PharmacySale, on_delete=models.CASCADE, related_name='items')
    medicine = models.ForeignKey(Medicine, on_delete=models.PROTECT)
    quantity = models.IntegerField(default=1)
    unit_price = models.DecimalField(max_digits=18, decimal_places=2)
    total = models.DecimalField(max_digits=18, decimal_places=2)

    def save(self, *args, **kwargs):
        self.total = self.quantity * self.unit_price
        super().save(*args, **kwargs)

# ==========================================
# 7. INPATIENT MANAGEMENT (IPD)
# ==========================================
class Ward(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Bed(models.Model):
    ward = models.ForeignKey(Ward, on_delete=models.CASCADE)
    room_number = models.CharField(max_length=50, blank=True, null=True)
    bed_number = models.CharField(max_length=50)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        room_info = f"Room {self.room_number} - " if self.room_number else ""
        return f"{self.ward.name} - {room_info}Bed {self.bed_number}"

class Admission(models.Model):
    STATUS_CHOICES = [
        ('Admitted', 'Admitted'),
        ('Discharged', 'Discharged')
    ]
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey('Doctor', on_delete=models.SET_NULL, null=True, blank=True)
    bed = models.ForeignKey(Bed, on_delete=models.PROTECT)
    admission_date = models.DateTimeField(default=timezone.now)
    expected_discharge_date = models.DateTimeField(null=True, blank=True)
    discharge_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Admitted')
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Admission #{self.id} of {self.patient.name} - Bed: {self.bed.bed_number}"

# ==========================================
# 8. BILLING AND FINANCE
# ==========================================
class Bill(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=18, decimal_places=2)
    is_paid = models.BooleanField(default=False)

# ==========================================
# 9. DASHBOARD & 10. REPORT
# ==========================================
class GeneratedReport(models.Model):
    report_type = models.CharField(max_length=100)
    generated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    generated_at = models.DateTimeField(auto_now_add=True)
    summary_data = models.TextField()