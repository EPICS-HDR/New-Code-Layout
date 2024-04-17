import io
from django.shortcuts import render
from services.backend.database.sqlclasses import find_data,find_data2, get_table_name
from django.core.paginator import Paginator
import xlsxwriter
from django.http import HttpResponse
from django import forms
from datetime import datetime, timedelta

locations = ["Hazen", "Stanton", "Washburn", "Price", "Bismarck", 
            "Schmidt", "Judson", "Mandan", "Breien", "Wakpala", "Little Eagle",
            "Cash", "Whitehorse", "Fort Peck", "Garrison", "Oahe", "Big Bend", 
            "Fort Randall", "Gavins Point", "Carson", "Fort Yates", "Linton", 
            "Mott"]
datasets = ["Gauge Height","Elevation", "Discharge", "Water Temperature", 
            "Flow Spill", "Flow Powerhouse", "Flow Out", "Tailwater Elevation", "Energy",
            "Air Temperature", "Average Air Temperature", "Average Relative Humidity", 
            "Average Bare Soil Temperature", "Average Turf Soil Temperature", "Maximum Wind Speed",
            "Average Wind Direction", "Total Solar Raditation", "Total Rainfall",
            "Average Baromatric Pressure", "Average Dew Point", "Average Wind Chill"]

prev_nav_map = {
    'time': 'location',
    'data': 'time',
    'selected_review': 'data',
}

next_nav_map = {
    'location': 'time',
    'time': 'data',
    'data': 'selected_review',
}

class LocationForm(forms.Form):
    location = forms.ChoiceField(
        required=True,
        widget=forms.Select(attrs={'class': 'form-control w-25 form-control-sm me-3'}),
        choices=[ (x,x) for x in locations ],
        )

def location_view(request):
    location = request.session.get('location')
    form = LocationForm(initial={'location': location})

    context = {
        'prev_nav': prev_nav_map.get('location'),
        'next_nav': next_nav_map.get('location'),
        'form': form,
    }
    return render(request, 'sources/location.html', context)

def time_view(request):
    if request.method == 'POST':
        request.session['location'] = request.POST['location']

    context = {
        'prev_nav': prev_nav_map.get('time'),
        'next_nav': next_nav_map.get('time'),
        'start_date' : request.session.get('start_date'),
        'end_date' : request.session.get('end_date'),
        'is_single' : request.session.get('is_single'),
    }
    return render(request, 'sources/time.html', context)

class DataForm(forms.Form):
    MY_CHOICES = (    )

    my_field = forms.MultipleChoiceField(
        label="select data to download",
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'flex'}), 
        choices=MY_CHOICES)

def data_view(request):
    if request.method == 'POST':
        request.session['start_date'] = request.POST['startDate']
        request.session['end_date'] = request.POST['endDate']
        request.session['display_format'] = request.POST['displayFormat']
        request.session['is_single'] = request.POST['isSingle'] == 'true'
        
    location = request.session.get('location')
    start_date = request.session.get('start_date')
    end_date = request.session.get('end_date')
    is_single = request.session.get('is_single')
    display_format = request.session.get('display_format')

    if is_single:
        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
        end_date = (start_date_obj + timedelta(days=1) - timedelta(seconds=1)).strftime("%Y-%m-%d %H:%M:%S")


    table_name = get_table_name(location)
    data = find_data(location, start_date, end_date)
    paginator = Paginator(data, 10)  # Show 10 items per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    print("data",len(data))
    columns = [] if len(data) == 0 else data[0].keys()

    print("data2see: ",location,start_date,end_date,display_format)

    form = DataForm(initial={'my_field': request.session.get('selected_fields')})
    form.fields['my_field'].choices = [(x,x) for x in columns[2:]]

    context = {
        'prev_nav': prev_nav_map.get('data'),
        'next_nav': next_nav_map.get('data'),
        'table_name':table_name,
        'colunms':columns,
        'form': form,
        'table': page_obj,
    }
    return render(request, 'sources/data.html', context)

def selected_review(request):
    if request.method == 'GET':
        if request.GET.getlist('my_field'):
            request.session['selected_fields'] = request.GET.getlist('my_field')

    location = request.session.get('location')
    start_date = request.session.get('start_date')
    end_date = request.session.get('end_date')
    selected_fields = request.session.get('selected_fields')

    is_single = request.session.get('is_single')
    if is_single:
        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
        end_date = (start_date_obj + timedelta(days=1) - timedelta(seconds=1)).strftime("%Y-%m-%d %H:%M:%S")


    print(selected_fields)
    columns = ['location','datetime']
    if selected_fields:
        columns.extend(selected_fields)
    table_name = get_table_name(location)
    data = find_data2(location, start_date, end_date,columns)
   
    print("data",len(data))

    paginator = Paginator(data, 10)  # Show 10 items per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.method == 'POST':
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet()

        for col_num, key in enumerate(columns):
            worksheet.write(0, col_num, key)

        for row_num, item in enumerate(data):
            for col_num, key in enumerate(columns):
                worksheet.write(row_num+1, col_num, item[key])

        workbook.close()
        output.seek(0)
        response = HttpResponse(output.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=data.xlsx'

        return response
    
    else:
        context = {
            'prev_nav': prev_nav_map.get('selected_review'),
            'next_nav': next_nav_map.get('selected_review'),
            'colunms':columns,
            'table': page_obj,

        }
        return render(request, 'sources/selected_review.html', context)
