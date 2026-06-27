from django.urls import path
from .views import schedule_view, vehicles_view

urlpatterns = [
    path('schedule', schedule_view, name='schedule'),
    path('vehicles', vehicles_view, name='vehicles'),
]