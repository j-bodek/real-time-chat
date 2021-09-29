from django.db import models

# Create your models here.

class PairedUser(models.Model):
    user_id = models.CharField(max_length=300, blank=True, null=True)
    stranger_id = models.CharField(max_length=300, blank=True, null=True)

class ActiveUser(models.Model):
    user_id = models.CharField(max_length=300, blank=True, null=True)

class OnlineUsers(models.Model):
    number = models.IntegerField()