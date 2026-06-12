from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Doctor, Nurse, Patient

# Isticmaal UserAdmin si aadan u helin qaladka 'AlreadyRegistered'
admin.site.register(User, UserAdmin)
admin.site.register(Doctor)
admin.site.register(Nurse)
admin.site.register(Patient)