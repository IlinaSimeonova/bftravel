from datetime import date

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect, render

from trip_planner.models import BookedTrip, VisitedPlace


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'login.html', {'form': {'errors': True}})

    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def home(request):
    # Get upcoming booked trips (start_date >= today)
    today = date.today()
    upcoming_trips = BookedTrip.objects.filter(start_date__gte=today).order_by('start_date')
    # Get current trip (today is between start and end)
    current_trip = BookedTrip.objects.filter(start_date__lte=today, end_date__gte=today).first()
    # Get past trips
    past_trips = BookedTrip.objects.filter(end_date__lt=today).order_by('-start_date')

    context = {
        'upcoming_trips': upcoming_trips,
        'current_trip': current_trip,
        'past_trips': past_trips,
    }
    return render(request, 'home.html', context)


def visited_places_api(request):
    """API endpoint that returns all visited places as JSON for the map."""
    places = VisitedPlace.objects.all()

    data = []
    for place in places:
        data.append({
            'id': place.id,
            'country': place.country,
            'city': place.city,
            'location': place.display_location,
            'latitude': float(place.latitude),
            'longitude': float(place.longitude),
            'date_visited': place.date_visited.isoformat(),
            'date_display': place.date_visited.strftime('%B %Y'),
            'photo_url': place.photo.url if place.photo else None,
            'notes': place.notes,
        })

    return JsonResponse({'places': data})


def mockup_fonts(request):
    return render(request, 'dev/mockups/fonts.html')


def mockup_layout(request):
    return render(request, 'dev/mockups/layout.html')
