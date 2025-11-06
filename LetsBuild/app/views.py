'''
Author: Quinn (gigawttz)

What it Does: passes requests to templates/app/.. and serves pages
'''


from django.shortcuts import render, redirect

from .forms import CreateUserForm, LoginForm

from django.http import HttpResponse, HttpRequest

from django.db.models import Count

from .models import Quiz, Question, Answer

from django.core.paginator import Paginator

from django.contrib.auth.models import auth

from django.contrib.auth import authenticate, login, logout

from typing import Optional


def homepage(request):

    return render(request, 'app/index.html')


def quiz(request):
    topics = Quiz.objects.all().annotate(questions_count=Count('question'))
    print("DEBUG topics count:", topics.count())
    return render(request, "app/quiz.html", {"topics": topics})

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
                    topics = Quiz.objects.all().annotate(questions_count= Count('question'))
                    return render(
                        request, 'quiz.html', context={'topics': topics}
                    )
                    
                
                else:
                    return redirect('dashboard')

    context = {'loginform': form}

    return render(request, 'app/login.html', context= context)

def get_questions(request, is_start= False) -> HttpResponse:

    
    if is_start:
        request = _reset_quiz(request)
        question = _get_first_question(request)

    else:
        question = _get_subsequent_question(request)

        if question is None:

            return get_finish(request)

    answers = Answer.objects.filter(question= question)
    request.session['question_id'] = question.id

    return render(request, 'app/question.html', context= {
        'question': question, 'answers': answers
    })

def _get_first_question(request) -> Question:

    quiz_id = request.POST['quiz_id']
    return Question.objects.filter(quiz_id= quiz_id).order_by('id').first()

def _get_subsequent_question(request) -> Optional[Question]:
    quiz_id = request.POST['quiz_id']
    previous_question_id = request.session['question_id']


    try:
        return Question.objects.filter(
            quiz_id= quiz_id, id__gt= previous_question_id
        ).order_by('id').first()

    except Question.DoesNotExist:
        return None

def get_answer(request) -> HttpResponse:

    submitted_answer_id = request.POST['answer_id']
    submitted_answer = Answer.objects.get(id= submitted_answer_id)


    if submitted_answer.is_correct:

        correct_answer = submitted_answer
        request.session['score'] = request.session.get('score', 0) + 1

    else:
        correct_answer = Answer.objects.get(
            question_id= submitted_answer.question_id, is_correct= True
        )

    return render(
        request, 'app/answer.html', context={
            'submitted_answer': submitted_answer,
            'answer': correct_answer,
        }
    )

def get_finish(request) -> HttpResponse:

    quiz = Question.objects.get(id= request.session['question_id']).quiz

    questions_count = Question.objects.filter(quiz=quiz).count()

    score = request.session.get('score', 0)

    percent = int(score / questions_count * 100)

    request = _reset_quiz(request)


    return render(request, 'app/finish.html', context= {
        'questions_count': questions_count, 'score': score, 'percent_score': percent
    })

def _reset_quiz(request) -> HttpRequest:


    if 'question_id' in request.session:
        del request.session['question_id']

    if 'score' in request.session:
        del request.session['score']

    return request

def dashboard(request):

    return render(request, 'app/dashboard.html')


def user_logout(request):

    auth.logout(request)

    return redirect("")

def go_to_register(request):

    return redirect("register")

def get_interests(request):
    return render(request, 'app/interests.html')