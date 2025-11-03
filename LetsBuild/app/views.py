'''
Author: Quinn (gigawttz)

What it Does: passes requests to templates/app/.. and serves pages
'''


from django.shortcuts import render, redirect

from .forms import CreateUserForm, LoginForm

from django.contrib.auth.models import auth

from django.contrib.auth import authenticate, login, logout


def homepage(request):

    return render(request, 'app/index.html')


def quiz(request):
    return render(request, "app/quiz.html")

def register(request):

    form = CreateUserForm()

    if request.method == "POST":
        

        form = CreateUserForm(request.POST)

        if form.is_valid():

            
            form.save()

            return redirect('/')


    context = {'registerform': form}

    return render(request, 'app/register.html', context= context)


def login(request):
    
    form = LoginForm()

    if request.method == "POST":

        form = LoginForm(request, data= request.POST)

        if form.is_valid():

            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(request, username= username, password= password)
            
            user_data = form.get_user()

            if user is not None:
                auth.login(request, user)

                if user_data.last_login is None:
                    return redirect('quiz')
                
                else:
                    return redirect('dashboard')

    context = {'loginform': form}

    return render(request, 'app/login.html', context= context)

def dashboard(request):

    return render(request, 'app/dashboard.html')


def user_logout(request):

    auth.logout(request)

    return redirect("")

def go_to_register(request):

    return redirect("register")

