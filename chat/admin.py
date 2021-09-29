from django.contrib import admin
from . models import PairedUser,ActiveUser

# Register your models here.

admin.site.register(PairedUser)
admin.site.register(ActiveUser)