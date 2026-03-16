from django.shortcuts import render


def home(request):
    return render(request, 'home.html')


def mockup_fonts(request):
    return render(request, 'dev/mockups/fonts.html')
