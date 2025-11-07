'''
Author: Quinn (gigawttz)

What it Does: passes requests to templates/app/.. and serves pages
'''


from django.shortcuts import render, redirect

from .forms import CreateUserForm, LoginForm

from django.http import HttpResponse, HttpRequest

from django.db.models import Count

from .models import Quiz, Question, Answer, SurveyAnswer, SurveySubmission

from django.core.paginator import Paginator

from django.contrib.auth.models import auth

from django.contrib.auth import authenticate, login, logout

from typing import Optional


def homepage(request):

    return render(request, 'app/index.html')


def quiz(request):
    topics = Quiz.objects.all().annotate(questions_count=Count('question'))
    
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


        submission = SurveySubmission.objects.create(
            user=request.user if request.user.is_authenticated else None,
            quiz=question.quiz,
        )
        request.session['submission_id'] = submission.id
    else:
 
        question = _get_subsequent_question(request)

        if question is None:

            return get_finish(request)


    request.session['question_id'] = question.id

    answers = Answer.objects.filter(question=question)

    return render(
        request,
        'app/question.html',  
        {
            'question': question,
            'answers': answers,
        },
    )

def _get_first_question(request) -> Question:
    quiz_id = request.POST['quiz_id']

    
    request.session['quiz_id'] = int(quiz_id)

    return (
        Question.objects
        .filter(quiz_id=quiz_id)
        .order_by('id')
        .first()
    )

def _get_subsequent_question(request) -> Optional[Question]:
    quiz_id = request.session['quiz_id']
    previous_question_id = request.session['question_id']

    return (
        Question.objects
        .filter(quiz_id=quiz_id, id__gt=previous_question_id)
        .order_by('id')
        .first())


    try:
        return Question.objects.filter(
            quiz_id= quiz_id, id__gt= previous_question_id
        ).order_by('id').first()

    except Question.DoesNotExist:
        return None

def get_answer(request) -> HttpResponse:

    # 1. Get which answer the user picked
    submitted_answer_id = request.POST['answer_id']
    submitted_answer = Answer.objects.select_related('question', 'question__quiz').get(
        id=submitted_answer_id
    )

    current_question = submitted_answer.question
    quiz = current_question.quiz

    # 2. Get the current SurveySubmission
    submission_id = request.session.get('submission_id')
    if submission_id is None:
        # Fallback: if somehow missing, create a new submission
        submission = SurveySubmission.objects.create(
            user=request.user if request.user.is_authenticated else None,
            quiz=quiz,
        )
        request.session['submission_id'] = submission.id
    else:
        submission = SurveySubmission.objects.get(id=submission_id)

    # 3. Save this answer in the DB
    SurveyAnswer.objects.create(
        submission=submission,
        question=current_question,
        answer=submitted_answer,
    )

    # 4. Hand control back to get_questions to get the next question
    #    (is_start=False -> uses _get_subsequent_question and then either
    #    renders question.html or goes to get_finish)
    return get_questions(request, is_start=False)

def get_finish(request) -> HttpResponse:
    
    quiz_id = request.session.get('quiz_id')

    if quiz_id:
        questions_count = Question.objects.filter(quiz_id=quiz_id).count()
    else:
        questions_count = 0

    responses = request.session.get('responses', [])
    responses_count = len(responses)

    # Clean up session
    request = _reset_quiz(request)

    return render(
        request,
        'app/interests.html',
        {
            'questions_count': questions_count,
            'responses_count': responses_count,
        }
    )

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

