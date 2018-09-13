from django.contrib import admin

from .models import SlackUser, Badge

admin.site.register(SlackUser)
admin.site.register(Badge)

# Register your models here.
