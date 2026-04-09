from django.core.management.base import BaseCommand

from trip_planner.models import Destination

DREAM_DESTINATIONS = [
    {
        "name": "Japan",
        "image_filename": "japan.jpg",
        "best_time": {
            "summary": "March to May (Spring) or October to November (Autumn)",
            "details": "Spring brings cherry blossoms and mild weather, while autumn offers stunning fall foliage. Both seasons have comfortable temperatures and fewer typhoons than summer."
        },
        "travel_tips": {
            "summary": "5 essential tips for Japan",
            "details": "• Get a JR Pass for unlimited train travel - saves money on bullet trains\n• Carry cash - many places don't accept cards\n• Learn basic phrases: Arigatou (thank you), Sumimasen (excuse me)\n• Remove shoes when entering homes, temples, and some restaurants\n• Bow slightly when greeting people"
        },
        "visa": {
            "summary": "Visa-free for both",
            "austrian": "No visa required for stays up to 90 days. Valid passport needed.",
            "bulgarian": "No visa required for stays up to 90 days. Valid passport needed."
        },
        "health": {
            "summary": "No special vaccines required",
            "details": "Japan has excellent healthcare. No mandatory vaccinations. Tap water is safe to drink. Pharmacies are well-stocked but staff may not speak English - bring translations of any medications you need."
        },
        "must_sees": {
            "summary": "Top 5 unmissable spots",
            "details": "1. Tokyo - Shibuya crossing, Senso-ji Temple, Tsukiji fish market\n2. Kyoto - Fushimi Inari shrine, Arashiyama bamboo grove\n3. Mount Fuji - iconic views, climbing season July-August\n4. Hiroshima - Peace Memorial, Miyajima Island\n5. Osaka - street food paradise, Osaka Castle"
        },
        "food": {
            "summary": "A culinary paradise",
            "details": "1. Ramen - rich noodle soup, try different regional styles\n2. Sushi - fresh and affordable at conveyor belt restaurants\n3. Okonomiyaki - savory pancakes, especially in Osaka\n4. Takoyaki - octopus balls, perfect street snack\n5. Wagyu beef - melt-in-your-mouth Japanese beef"
        },
        "budget": {
            "summary": "€80-120 per day",
            "details": "Accommodation: €40-80 (hostels €25, mid-range hotels €60-100)\nFood: €20-40 (cheap eats €5-10, restaurants €15-25)\nTransport: €15-30 (JR Pass averages €20/day)\nActivities: €10-20 (many temples free, museums €5-15)"
        }
    },
    {
        "name": "Nepal",
        "image_filename": "nepal.jpg",
        "best_time": {
            "summary": "October to November (Autumn) or March to April (Spring)",
            "details": "Autumn offers clear skies and perfect trekking conditions after monsoon. Spring brings blooming rhododendrons and warmer temperatures. Avoid monsoon season (June-September)."
        },
        "travel_tips": {
            "summary": "5 essential tips for Nepal",
            "details": "• Acclimatize properly if trekking at altitude - never rush\n• Bargain at markets but be fair - a few rupees matter more to locals\n• Carry toilet paper and hand sanitizer outside cities\n• Dress modestly at temples, remove shoes before entering\n• Namaste (hands together, slight bow) is the standard greeting"
        },
        "visa": {
            "summary": "Visa on arrival for both",
            "austrian": "Visa on arrival available. 15 days ($30), 30 days ($50), 90 days ($125). Passport photo required.",
            "bulgarian": "Visa on arrival available. 15 days ($30), 30 days ($50), 90 days ($125). Passport photo required."
        },
        "health": {
            "summary": "Recommended: Hepatitis A, Typhoid",
            "details": "Recommended vaccines: Hepatitis A & B, Typhoid, Tetanus. Consider altitude sickness medication if trekking. Don't drink tap water - stick to bottled or purified. Travel insurance with evacuation coverage essential for trekking."
        },
        "must_sees": {
            "summary": "Top 5 unmissable spots",
            "details": "1. Everest Base Camp Trek - iconic 2-week adventure\n2. Kathmandu - Durbar Square, Boudhanath Stupa, Swayambhunath\n3. Pokhara - lakeside relaxation, Annapurna views\n4. Chitwan National Park - jungle safaris, rhinos, tigers\n5. Annapurna Circuit - diverse landscapes, Thorong La pass"
        },
        "food": {
            "summary": "Hearty mountain cuisine",
            "details": "1. Dal Bhat - lentil soup with rice, unlimited refills\n2. Momos - Tibetan dumplings, Nepal's favorite snack\n3. Thukpa - hearty noodle soup perfect after trekking\n4. Sel Roti - sweet rice bread, traditional snack\n5. Yak cheese - try it in the mountains"
        },
        "budget": {
            "summary": "€30-50 per day",
            "details": "Accommodation: €10-25 (guesthouses €5-15, mid-range €20-40)\nFood: €8-15 (local meals €2-5, restaurants €8-12)\nTransport: €5-10 (buses cheap, domestic flights €80-150)\nTrekking permits: €25-50 depending on area"
        }
    },
    {
        "name": "Mexico",
        "image_filename": "mexico-taco.jpg",
        "best_time": {
            "summary": "December to April (Dry Season)",
            "details": "Dry season offers sunny days and pleasant temperatures. Coastal areas warm year-round. Avoid hurricane season (June-November) on Caribbean coast. Shoulder months (May, November) offer fewer crowds and decent weather."
        },
        "travel_tips": {
            "summary": "5 essential tips for Mexico",
            "details": "• Learn basic Spanish - English isn't widely spoken outside tourist areas\n• Don't drink tap water - stick to bottled (agua purificada)\n• Use Uber or official taxis (sitio) for safety\n• Carry small bills - many places can't break large notes\n• Sunscreen and bug spray are essentials"
        },
        "visa": {
            "summary": "Visa-free for both",
            "austrian": "No visa required for stays up to 180 days. Tourist card (FMM) issued on arrival.",
            "bulgarian": "No visa required for stays up to 180 days. Tourist card (FMM) issued on arrival."
        },
        "health": {
            "summary": "Recommended: Hepatitis A, Typhoid",
            "details": "Recommended vaccines: Hepatitis A, Typhoid. Traveler's diarrhea common - be careful with street food initially. Stay hydrated. Mosquito repellent important in jungle/coastal areas. Good healthcare available in cities."
        },
        "must_sees": {
            "summary": "Top 5 unmissable spots",
            "details": "1. Mexico City - Zocalo, Frida Kahlo museum, incredible food scene\n2. Oaxaca - indigenous culture, mezcal, stunning crafts\n3. Yucatan - Chichen Itza, cenotes, Mayan ruins\n4. Guanajuato - colorful colonial city, underground streets\n5. Tulum - beach ruins, bohemian vibes, cenote swimming"
        },
        "food": {
            "summary": "World-class cuisine",
            "details": "1. Tacos al Pastor - spit-roasted pork with pineapple\n2. Mole - complex sauce with chocolate and chilies\n3. Ceviche - fresh lime-cured seafood\n4. Tamales - steamed corn dough with fillings\n5. Churros con chocolate - fried dough with thick hot chocolate"
        },
        "budget": {
            "summary": "€40-70 per day",
            "details": "Accommodation: €15-35 (hostels €10-15, hotels €25-50)\nFood: €10-20 (street food €2-5, restaurants €8-15)\nTransport: €10-15 (buses very affordable, Uber cheap)\nActivities: €5-20 (ruins €5-10, cenotes €5-15)"
        }
    },
    {
        "name": "Madagascar",
        "image_filename": "madagascar.jpg",
        "best_time": {
            "summary": "April to October (Dry Season)",
            "details": "Dry season offers pleasant weather and easier travel conditions. Wildlife viewing best April-May and September-October. Avoid cyclone season (January-March) especially on east coast. Whale watching July-September."
        },
        "travel_tips": {
            "summary": "5 essential tips for Madagascar",
            "details": "• Book internal flights early - they fill up fast\n• Roads are rough - 4WD recommended, travel times longer than expected\n• Bring cash (Ariary) - ATMs unreliable outside cities\n• Learn French basics - more useful than English\n• Hire local guides - required in parks, supports communities"
        },
        "visa": {
            "summary": "Visa on arrival for both",
            "austrian": "Visa on arrival. Up to 30 days (~€25), 60 days (~€45). Passport with 6 months validity required.",
            "bulgarian": "Visa on arrival. Up to 30 days (~€25), 60 days (~€45). Passport with 6 months validity required."
        },
        "health": {
            "summary": "Malaria prophylaxis recommended",
            "details": "Malaria present - take prophylaxis and use repellent. Recommended vaccines: Hepatitis A & B, Typhoid, Yellow Fever (if coming from affected country). Drink only bottled water. Medical facilities limited outside Antananarivo."
        },
        "must_sees": {
            "summary": "Top 5 unmissable spots",
            "details": "1. Avenue of the Baobabs - iconic sunset views\n2. Andasibe - indri lemurs, rainforest walks\n3. Isalo National Park - dramatic canyons, swimming holes\n4. Nosy Be - beaches, snorkeling, whale sharks\n5. Tsingy de Bemaraha - unique limestone formations"
        },
        "food": {
            "summary": "Rice-based cuisine with French influence",
            "details": "1. Romazava - national dish, meat and greens stew\n2. Ravitoto - cassava leaves with pork\n3. Zebu steak - local beef, very tender\n4. Mofo gasy - street-side rice cakes\n5. Fresh seafood - lobster incredibly affordable on coast"
        },
        "budget": {
            "summary": "€50-80 per day",
            "details": "Accommodation: €20-40 (basic €10-20, mid-range €30-60)\nFood: €10-15 (local meals €3-5, restaurants €8-15)\nTransport: €15-25 (4WD hire essential for many areas)\nPark fees & guides: €15-30 per park"
        }
    },
    {
        "name": "South Korea",
        "image_filename": "korea.jpg",
        "best_time": {
            "summary": "April to May (Spring) or September to November (Autumn)",
            "details": "Spring brings cherry blossoms and mild weather. Autumn offers stunning fall foliage and harvest festivals. Summer is hot and humid with monsoon rains. Winter is cold but great for skiing and fewer tourists."
        },
        "travel_tips": {
            "summary": "5 essential tips for South Korea",
            "details": "• Get a T-money card for all public transport\n• Download Naver Maps - Google Maps doesn't work well here\n• Wi-Fi is everywhere, but get a SIM for convenience\n• Bow slightly when greeting or thanking someone\n• Shoes off when entering homes and some traditional restaurants"
        },
        "visa": {
            "summary": "Visa-free for both",
            "austrian": "No visa required for stays up to 90 days. K-ETA required (electronic travel authorization, ~€7).",
            "bulgarian": "No visa required for stays up to 90 days. K-ETA required (electronic travel authorization, ~€7)."
        },
        "health": {
            "summary": "No special vaccines required",
            "details": "No mandatory vaccinations. Excellent healthcare system. Tap water is safe but most locals drink filtered. Air quality can be poor - check AQI and bring masks if sensitive. Pharmacies well-stocked."
        },
        "must_sees": {
            "summary": "Top 5 unmissable spots",
            "details": "1. Seoul - Gyeongbokgung Palace, Bukchon Hanok Village, nightlife\n2. Busan - beaches, Gamcheon Culture Village, seafood markets\n3. Jeju Island - volcanic landscapes, beaches, unique culture\n4. DMZ - sobering look at divided Korea\n5. Gyeongju - ancient capital, temples, royal tombs"
        },
        "food": {
            "summary": "Bold flavors and BBQ heaven",
            "details": "1. Korean BBQ - grill your own meat at the table\n2. Bibimbap - rice bowl with vegetables and gochujang\n3. Kimchi - fermented vegetables with every meal\n4. Tteokbokki - spicy rice cakes, popular street food\n5. Fried chicken & beer (chimaek) - Korean institution"
        },
        "budget": {
            "summary": "€60-100 per day",
            "details": "Accommodation: €25-50 (guesthouses €20-30, hotels €40-80)\nFood: €15-25 (street food €3-8, restaurants €10-20)\nTransport: €10-20 (subway cheap, KTX trains €30-50)\nActivities: €10-20 (palaces €3-5, DMZ tour €40-60)"
        }
    }
]


class Command(BaseCommand):
    help = 'Seed the database with dream destination data'

    def handle(self, *args, **options):
        for dest_data in DREAM_DESTINATIONS:
            destination, created = Destination.objects.update_or_create(
                name=dest_data['name'],
                defaults={
                    'best_time': dest_data['best_time'],
                    'travel_tips': dest_data['travel_tips'],
                    'visa': dest_data['visa'],
                    'health': dest_data['health'],
                    'must_sees': dest_data['must_sees'],
                    'food': dest_data['food'],
                    'budget': dest_data['budget'],
                    'image_filename': dest_data.get('image_filename', ''),
                    'is_dream_destination': True,
                }
            )
            status = 'Created' if created else 'Updated'
            self.stdout.write(f'{status}: {destination.name}')

        self.stdout.write(self.style.SUCCESS('Successfully seeded dream destinations'))
