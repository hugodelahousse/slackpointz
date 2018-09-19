from django.contrib import admin
from .models import SlackUser, QuotzSubscription

admin.site.register(SlackUser)
admin.site.register(QuotzSubscription)

# Register your models here.
