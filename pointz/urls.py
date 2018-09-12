from django.urls import path
from .views import slash_pointz

urlpatterns = [
    path('', slash_pointz)
]
