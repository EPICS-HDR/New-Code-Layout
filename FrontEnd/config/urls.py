"""project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from FrontEnd.services.views import (
    about,
    api_map_locations,
    api_timeseries,
    contactus,
    customcocograph,
    customgaugegraph,
    custommesonetgraph,
    customnoaagraph,
    customshadehillgraph,
    forecast,
    generate_maptab_graph,
    get_latest_date,
    health,
    homepage,
    interactiveMap,
    maptabs,
    test,
)

urlpatterns = [
    path('admin/', include('FrontEnd.admin_dashboard.urls')),
    path('customgaugegraph/', customgaugegraph),
    path('customcocograph/', customcocograph),
    path('customnoaagraph/', customnoaagraph),
    path('custommesonetgraph/', custommesonetgraph),
    path('customshadehillgraph/', customshadehillgraph),
    path('map/', interactiveMap),
    path('health', health),
    path('homep/', test),
    path('home/', homepage),
    path('maptabs/', maptabs),
    path('generate_maptab_graph/', generate_maptab_graph),
    path('get_latest_date/', get_latest_date),
    path('api/map_locations/', api_map_locations),
    path('api/timeseries/', api_timeseries),
    path('', homepage),
    path('forecast/', forecast),
    path('about/', about),
    path('contactus/', contactus, name='contactus'),
]

urlpatterns += staticfiles_urlpatterns()
