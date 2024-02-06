from plotly.offline import plot
from plotly.graph_objs import Scatter
import os
from datetime import datetime
import json
from .backend.database.sqlclasses import dictpull, moving_average
from .backend.graphgeneration.createCustom import customGraph, makeTable
from django.template.defaulttags import csrf_token
from config import settings
from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail

# Create your views here.
def register(request):
    return render(request, "HTML/register.html")

def signup(request):

    if request.method == "POST":
        username = request.POST['username']
        fname = request.POST['fname']
        lname = request.POST['lname']
        email = request.POST['email']
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']

                
        if User.objects.filter(username=username):
            messages.error(request, "Username already exist! Please try some other username.")
            return redirect('home')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email Already Registered!!")
            return redirect('home')
        
        if len(username)>20:
            messages.error(request, "Username must be under 20 charcters!!")
            return redirect('home')
        
        if pass1 != pass2:
            messages.error(request, "Passwords didn't matched!!")
            return redirect('home')
        
        if not username.isalnum():
            messages.error(request, "Username must be Alpha-Numeric!!")
            return redirect('home')
        
        myuser = User.objects.create_user(username, email, pass1)
        myuser.first_name = fname
        myuser.last_name = lname

        myuser.save()

        messages.success(request, "Your account has been succefully created. We have sent you a confirmation email, please confirm your email in order to activate your account")

        #Welcome email

        subject = "Welcome to HDR - Django Login!"
        message = "Hello" + myuser.first_name + "!! \n" + "Welcome to HDR!! \n Thank you for visiting our website \n We habe also sent you a confirmation email, please comfirm email adress in order to activate your account. \n\n Thanking you \n HDR TEAM"
        from_email = settings.EMAIL_HOST_USER
        to_list = [myuser.email]
        send_mail(subject, message, from_email, to_list, fail_silently = True)

        return redirect('signin')

    return render(request, "HTML/signup.html")

def signin(request):
    if request.method == 'POST':
        username = request.POST['username']
        pass1 = request.POST['pass1']
        
        user = authenticate(username=username, password=pass1)
        
        if user is not None:
            login(request, user)
            fname = user.first_name
            
            return render(request, "HTML/register.html",{"fname":fname})
        else:
            messages.error(request, "Bad Credentials!!")
            return redirect('home')
    
    return render(request, "HTML/signin.html")

def signout(request):
    logout(request)
    messages.success(request, "Logged Out Successfully")
    return redirect('/register')

def about(request):
    return render(request, 'HTML/about.html')

def forecast(request):
    return render(request, 'HTML/forecast.html')

def homepage(request):
    return render(request, 'HTML/homepage.html')

def maptabs(request):
    return render(request, 'HTML/maptabs.html')
    
def tabs(request):
    return render(request, 'graphing/tabs.html')

def tabstest(request):
    return render(request, 'graphing/tabstest.html')

def test(request):
    return render(request, 'graphing/test.html')

def customgauge(request):
    return render(request, 'graphing/customgauge.html')

def customdam(request):
    return render(request, 'graphing/customdam.html')

def custommesonet(request):
    return render(request, 'graphing/custommesonet.html')

def index(request):
    
    return render(request, 'HTML/index.html')

def customgaugegraph(request):
    
    #Pulls most recently submitted data
    locationlist = request.POST.getlist('location')
    length = len(locationlist)

    data2see = request.POST['data2see']

    start_date = request.POST['start-date']

    end_date = request.POST['end-date']

    datalist = []
    sites = []
    index = 0
    while index < length:
        locations = locationlist[index]
        locations = locations.split()
        if locations[0] == "Little":
            locations[0] = "Little Eagle"
        sites.append(locations[0])
        times, data = dictpull(locations[0], data2see, start_date, end_date)
        m = moving_average()
        m_t, m_d = m.one_day_ma(times,data)
        datalist.append(data)
        index += 1
        
    plot = customGraph(times, sites, datalist, data2see)
    table = makeTable(datalist)

    return render(request, "HTML/graphdisplay.html", context={'plot': plot, 'table': table})

def customdamgraph(request):

    locationlist = request.POST.getlist('dam')
    length = len(locationlist)
    data2see = request.POST['data2see']
    if "_" in data2see:
        data2see = data2see.split("_")
        data2see = data2see[0] + " " + data2see[1]

    start_date = request.POST['start-date']

    end_date = request.POST['end-date']

    folder_path = "./map/static/customdata/"

    datalist = []
    sites = []
    index = 0
    while index < length:
        sites.append(locationlist[index])
        times, data = dictpull(locationlist[index], data2see, start_date, end_date)
        datalist.append(data)
        index += 1
        
    plot = customGraph(times, sites, datalist, data2see)
    table = makeTable(datalist)

    return render(request, 'HTML/graphdisplay.html', context={'plot': plot, 'table': table})

def custommesonetgraph(request):

    locationlist = request.POST.getlist('mesonet')
    length = len(locationlist)
    data2see = request.POST['data2see']
    if "_" in data2see:
        data2see = data2see.split("_")
        data2see = data2see[0] + " " + data2see[1]

    start_date = request.POST['start-date']

    end_date = request.POST['end-date']

    datalist = []
    sites = []
    index = 0
    while index < length:
        sites.append(locationlist[index])
        times, data = dictpull(locationlist[index], data2see, start_date, end_date)
        datalist.append(data)
        index += 1
        
    plot = customGraph(times, sites, datalist, data2see)
    table = makeTable(datalist)

    return render(request, 'HTML/graphdisplay.html', context={'plot': plot, 'table': table})
