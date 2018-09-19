from django.urls import path
from .views import slash_bookzsubscribe

urlpatterns = [
    path('bookzsubscribe/', slash_bookzsubscribe),
]
