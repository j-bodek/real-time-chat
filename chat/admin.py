from django.contrib import admin
from . models import PairedUser,ActiveUser,OnlineUsers

# Register your models here.

admin.site.register(PairedUser)
admin.site.register(ActiveUser)
admin.site.register(OnlineUsers)