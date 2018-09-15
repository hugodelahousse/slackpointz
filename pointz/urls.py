from django.urls import path
from .views import slash_pointz, slash_badgz, slash_rankingz

urlpatterns = [
    path('pointz/', slash_pointz),
    path('badgz/', slash_badgz),
    path('rankingz/', slash_rankingz),
]
