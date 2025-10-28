'''
Author: Quinn (gigawttz)

What it Does: passes requests to templates/app/.. and serves pages
'''


from django.shortcuts import render, redirect

from .forms import CreateUserForm


def homepage(request):

    return render(request, 'app/index.html')

def register(request):

    form = CreateUserForm()

    if request.method == "POST":
        

        form = CreateUserForm(request.POST)

        if form.is_valid():

            
            form.save()

            return redirect('login')


    context = {'registerform': form}

    return render(request, 'app/register.html', context= context)


def login(request):

    return render(request, 'app/login.html')

def dashboard(request):

    return render(request, 'app/dashboard.html')