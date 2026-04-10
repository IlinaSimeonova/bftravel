import json
import logging
import re

import anthropic
from decouple import config
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from .models import BookedTrip, Destination, VisitedPlace, WoodyChat
from .services import get_destination_info

WOODY_SYSTEM_PROMPT = """You are Woody, a friendly and knowledgeable travel assistant for Dessi & Martin's travel website.

ABOUT DESSI & MARTIN:
- Martin is from Austria, Dessi is from Bulgaria
- They got married in January 2026
- They are adventure travelers: certified divers, hikers, climbers
- They stay in budget-friendly hotels and Airbnbs
- They travel light - carry-on only when possible
- Big foodies who love Asian cuisine especially
- They love beer
- They speak Bulgarian, German, and English
- They enjoy impressive cultural sites like temples
- They like a mix of active days and relaxation days
- Flexible with schedules - can party late or wake at 4am for adventures
- Dessi is afraid of heights (keep this in mind for recommendations)
- They have a car but mostly use it for trips in Austria

YOUR PERSONALITY:
- Friendly, enthusiastic, but not over the top
- Give practical, actionable advice
- Keep responses concise - they're planning, not reading a novel
- Use their names naturally in conversation
- If recommending activities, remember Dessi's fear of heights
- Suggest budget-friendly options when relevant
- Recommend local food spots and craft beer places when appropriate

When answering questions about a destination, be specific and helpful. If you don't know something, say so rather than making things up."""

logger = logging.getLogger(__name__)


def extract_json(text: str) -> dict | None:
    """Extract JSON from text that might have extra content around it."""
    # Try direct parse first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try to find JSON object in the text
    match = re.search(r'\{[\s\S]*\}', text)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    return None


def plan_trip(request):
    """Main trip planning page with destination search."""
    # Get all dream destinations for the template
    dream_destinations = Destination.objects.filter(is_dream_destination=True)

    context = {
        "destination": None,
        "sections": None,
        "dream_destinations": dream_destinations,
    }

    if request.method == "POST":
        destination_name = request.POST.get("destination", "").strip()
        if destination_name:
            # Check cache first (case-insensitive)
            cached = Destination.objects.filter(name__iexact=destination_name).first()

            if cached:
                # Use cached data
                context["destination"] = cached.name
                context["sections"] = {
                    "best_time": cached.best_time,
                    "travel_tips": cached.travel_tips,
                    "visa": cached.visa,
                    "health": cached.health,
                    "must_sees": cached.must_sees,
                    "food": cached.food,
                    "budget": cached.budget,
                }
                context["destination_obj"] = cached
            else:
                # Fetch from API and cache
                result = get_destination_info(destination_name)
                if result["success"]:
                    sections = extract_json(result["content"])
                    if sections:
                        # Save to cache
                        new_dest = Destination.objects.create(
                            name=destination_name,
                            best_time=sections.get("best_time", {}),
                            travel_tips=sections.get("travel_tips", {}),
                            visa=sections.get("visa", {}),
                            health=sections.get("health", {}),
                            must_sees=sections.get("must_sees", {}),
                            food=sections.get("food", {}),
                            budget=sections.get("budget", {}),
                            is_dream_destination=True,  # Auto-add to dream list
                        )
                        context["destination"] = destination_name
                        context["sections"] = sections
                        context["destination_obj"] = new_dest
                    else:
                        logger.error(f"Failed to parse AI response: {result['content'][:500]}")
                        context["error"] = "Could not parse travel information. Please try again."
                        context["destination"] = destination_name
                else:
                    context["error"] = "Could not get travel information. Please try again."
                    context["destination"] = destination_name

    return render(request, "trip_planner/plan_trip.html", context)


@require_POST
def book_trip(request):
    """Handle the 'I booked it!' button click - save trip to database."""
    destination = request.POST.get("destination", "").strip()
    start_date = request.POST.get("start_date")
    end_date = request.POST.get("end_date")

    if destination and start_date and end_date:
        BookedTrip.objects.create(
            destination=destination,
            start_date=start_date,
            end_date=end_date,
        )
        return redirect("home")

    # If missing data, redirect back to plan trip
    return redirect("trip_planner:plan_trip")


@require_POST
def upload_destination_photo(request, destination_id):
    """Handle photo upload for a destination."""
    try:
        destination = Destination.objects.get(id=destination_id)
    except Destination.DoesNotExist:
        return redirect("trip_planner:plan_trip")

    if 'photo' in request.FILES:
        destination.photo = request.FILES['photo']
        destination.save()

    return redirect("trip_planner:plan_trip")


@require_POST
def delete_destination(request, destination_id):
    """Delete a destination from the dream list."""
    try:
        destination = Destination.objects.get(id=destination_id)
        destination.delete()
    except Destination.DoesNotExist:
        pass

    return redirect("trip_planner:plan_trip")


@require_POST
def woody_chat(request):
    """Handle chat messages with Woody AI assistant."""
    try:
        data = json.loads(request.body)
        message = data.get('message', '').strip()
        destination = data.get('destination', '').strip()

        if not message:
            return JsonResponse({'error': 'Message is required'}, status=400)

        if not destination:
            return JsonResponse({'error': 'Destination is required'}, status=400)

        # Save user message to database
        WoodyChat.objects.create(
            destination=destination,
            role='user',
            content=message
        )

        # Load chat history from database
        history = WoodyChat.objects.filter(destination=destination).order_by('created_at')
        messages = [{"role": msg.role, "content": msg.content} for msg in history]

        # Build system prompt with destination context
        system = WOODY_SYSTEM_PROMPT

        # Add visited places to context
        visited = VisitedPlace.objects.values_list('country', flat=True).distinct()
        if visited:
            visited_list = ", ".join(visited)
            system += f"\n\nPLACES THEY'VE ALREADY VISITED: {visited_list}. You can reference these when relevant - compare destinations, mention their experience, or avoid suggesting places they've been unless they ask."

        system += f"\n\nCURRENT DESTINATION: The user is currently looking at {destination}. Focus your answers on this destination unless they ask about something else."

        # Call Claude API
        api_key = config('ANTHROPIC_API_KEY')
        client = anthropic.Anthropic(api_key=api_key)

        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            system=system,
            messages=messages
        )

        assistant_response = response.content[0].text

        # Save assistant response to database
        WoodyChat.objects.create(
            destination=destination,
            role='assistant',
            content=assistant_response
        )

        return JsonResponse({
            'response': assistant_response,
            'success': True
        })

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"Woody chat error: {e}")
        return JsonResponse({'error': 'Something went wrong'}, status=500)


def woody_chat_history(request, destination):
    """Load chat history for a destination."""
    messages = WoodyChat.objects.filter(destination=destination).order_by('created_at')
    return JsonResponse({
        'messages': [{'role': msg.role, 'content': msg.content} for msg in messages],
        'success': True
    })
