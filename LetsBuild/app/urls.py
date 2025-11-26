from django.urls import path

from . import views


urlpatterns = [
    
    path("homepage", views.homepage, name= "homepage"), #routes to homepage

    path("register", views.register, name= "register"),

    path("", views.login, name= ""),

    path("dashboard", views.dashboard, name= "dashboard"),

    path("user-logout", views.user_logout, name= "user-logout"),

    path("go-to-register", views.go_to_register, name= "go-to-register"),

    path("quiz", views.quiz, name= "quiz"),

    path('get-questions', views.get_questions, {'is_start': True}, name= 'get-questions'),

    path('get-questions-next', views.get_questions, {'is_start': False}, name='get-questions-next'),

    path('get-answer', views.get_answer, name='get-answer'),

    path('get-finish', views.get_finish, name='get-finish'),

    path('interests', views.get_interests, name='interests'),

    path("save-interests", views.save_interests, name="save-interests"),

    path("save-project", views.save_chosen_project, name="save-project"),

    path("index", views.index, name="index"),

    path("rec-view", views.rec_view, name="rec-view"),

    path("get-more-steps", views.get_more_steps, name="get-more-steps")

]
