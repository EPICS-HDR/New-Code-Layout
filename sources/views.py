from django.shortcuts import render


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


def location_view(request):

    context = {
        'prev_nav': prev_nav_map.get('location'),
        'next_nav': next_nav_map.get('location'),
    }
    
    return render(request, 'sources/location.html', context)

def time_view(request):
    context = {
        'prev_nav': prev_nav_map.get('time'),
        'next_nav': next_nav_map.get('time'),
    }
    return render(request, 'sources/time.html', context)

def data_view(request):
    context = {
        'prev_nav': prev_nav_map.get('data'),
        'next_nav': next_nav_map.get('data'),
    }
    return render(request, 'sources/data.html', context)

def selected_review(request):
    context = {
        'prev_nav': prev_nav_map.get('selected_review'),
        'next_nav': next_nav_map.get('selected_review'),
    }
    return render(request, 'sources/selected_review.html', context)
