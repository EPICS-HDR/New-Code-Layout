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
from django.urls import path
from services.views import index, customgauge, customgaugegraph, customdam, customdamgraph, test, custommesonet, custommesonetgraph, tabs, tabstest, maptabs, homepage, forecast, about, register, signup, signin, signout, vansh
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from services import views  # Import the views module containing your view functions
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('customgaugegraph/', customgaugegraph),
    path('customdamgraph/', customdamgraph),
#    path('customgauge/', customgauge),
    path('customdam/', customdam),
#    path('custommesonet/', custommesonet),
    path('custommesonetgraph/', custommesonetgraph),
    path('map/', index),
    path('homep/', test),
#    path('tabs/', tabs),
#    path('tabstest/', tabstest),
    path('maptabs/', maptabs),
    path('home/', homepage),
    path('forecast/', forecast),
    path('about/', about),
    path('register/', register),
    path('signup', signup, name='signup'),
    path('signin', signin, name='signin'),
    path('signout', signout, name='signout'),
    path('favorites/', views.favorites, name='favorites'),
    path('vansh/', vansh)
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

urlpatterns += staticfiles_urlpatterns()
