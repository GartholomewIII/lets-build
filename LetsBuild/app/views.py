from django.shortcuts import render

from django.http import HttpResponse
'''
Author: Quinn (gigawttz)

What it Does: passes requests to templates/app/.. and serves pages
'''

def homepage(request):

    return render(request, 'app/index.html')

def register(request):

    return render(request, 'app/register.html')


def login(request):

    return render(request, 'app/login.html')

def dashboard(request):

    return render(request, 'app/dashboard.html')