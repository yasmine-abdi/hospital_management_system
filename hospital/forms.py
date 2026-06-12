from django import forms
from .models import Patient, Doctor, Specialization, Appointment

class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        # Halkan ku dar field-yada aad ku leedahay model-kaaga
        fields = ['name', 'age', 'gender', 'address', 'phone', 'doctor']
        
        # Halkan waxaad ku qurxin kartaa CSS-ka form-ka
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Magaca Bukaanka'}),
            'age': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Da\'da'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Cinwaanka'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Lambarka Telefoonka'}),
        }
        
class DoctorForm(forms.ModelForm):
    full_name = forms.CharField(max_length=150, label='Fullname (Magaca Buuxa)', widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Geli magaca buuxa ee dhakhtarka'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Haddii xogta la bedelayo (update), magaca horay ugu jirtay soo saar
        if self.instance and self.instance.pk and self.instance.user:
            self.fields['full_name'].initial = f"{self.instance.user.first_name} {self.instance.user.last_name}".strip() or self.instance.user.username
        
    class Meta:
        model = Doctor
        fields = ['specialization', 'phone', 'shift_start', 'shift_end', 'is_available']
        
        labels = {
            'specialization': 'Takhasuska (Specialization)',
            'phone': 'Lambarka Telefoonka',
            'shift_start': 'Saacadda uu Bilaabayo',
            'shift_end': 'Saacadda uu Bixi doono',
            'is_available': 'Wuu Joogaa (Available)'
        }
        
        widgets = {
            'specialization': forms.Select(attrs={'class': 'form-select form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Geli talefoonka dhakhtarka'}),
            'shift_start': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'shift_end': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'is_available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def save(self, commit=True):
        doctor = super().save(commit=False)
        full_name = self.cleaned_data.get('full_name').strip()
        names = full_name.split(' ', 1)
        first_name = names[0]
        last_name = names[1] if len(names) > 1 else ''

        if not doctor.pk:
            # Haddii dhakhtar cusub la diiwaangelinayo, samee User account cusub
            from django.contrib.auth import get_user_model
            User = get_user_model()
            base_username = first_name.lower()
            username = base_username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1
            
            user = User.objects.create_user(
                username=username, 
                password='password123', # Password kumeel gaar ah
                first_name=first_name, 
                last_name=last_name, 
                role='Doctor'
            )
            doctor.user = user
        else:
            # Haddii magaca la bedelayo, cusboonaysii User-ka
            doctor.user.first_name = first_name
            doctor.user.last_name = last_name
            doctor.user.save()

        if commit:
            doctor.save()
        return doctor

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['patient', 'doctor', 'appointment_date', 'status']
        labels = {
            'patient': 'Bukaanka (Patient)',
            'doctor': 'Dhakhtarka (Doctor)',
            'appointment_date': 'Taariikhda iyo Saacadda (Date & Time)',
            'status': 'Xaaladda (Status)'
        }
        widgets = {
            'patient': forms.Select(attrs={'class': 'form-select form-control'}),
            'doctor': forms.Select(attrs={'class': 'form-select form-control'}),
            'appointment_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'status': forms.Select(attrs={'class': 'form-select form-control'}),
        }