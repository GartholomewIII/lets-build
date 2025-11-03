from django.urls import path

from . import views


urlpatterns = [
    
    path("homepage", views.homepage, name= "homepage"), #routes to homepage

    path("register", views.register, name= "register"),

    path("", views.login, name= ""),

    path("dashboard", views.dashboard, name= "dashboard"),

    path("user-logout", views.user_logout, name= "user-logout"),

    path("go-to-register", views.go_to_register, name= "go-to-register"),

    path("quiz", views.quiz, name= "quiz")

]
