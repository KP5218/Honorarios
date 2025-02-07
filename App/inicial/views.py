from django.contrib.auth import logout
from django.http import HttpRequest
from django.shortcuts import render, redirect


# Create your views here.
def home(request):
    """Renders the home page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/index.html',
        {
            'title':'Home Page',
        }
    )

def exit(request):
    logout(request)
    return redirect('home')