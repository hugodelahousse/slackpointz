from django.urls import path
from .views import slash_pointz, slash_badgz

urlpatterns = [
    path('pointz/', slash_pointz),
    path('badgz/', slash_badgz),
]
