from django.contrib import admin
from .models import User,MobileVerification,Follower,Event, Notification

admin.site.register(User)
admin.site.register(MobileVerification)
admin.site.register(Follower)
admin.site.register(Event)
admin.site.register(Notification)
# Register your models here.
