from django.urls import path
from .views import location_view, time_view, data_view, selected_review

urlpatterns = [
    path('location/', location_view, name='location'),
    path('time/', time_view, name='time'),
    path('data/', data_view, name='data'),
    path('selected-review/', selected_review, name='selected_review'),
]
