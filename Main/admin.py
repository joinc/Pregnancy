from django.contrib import admin
from Main.models import UserProfile, Resident, Reference, Logs

admin.site.register(UserProfile)
admin.site.register(Resident)
admin.site.register(Reference)
admin.site.register(Logs)
