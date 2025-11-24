'''
Author: Quinn (gigawttz)

What it Does: passes requests to templates/app/.. and serves pages
'''


from django.shortcuts import render, redirect

from .forms import CreateUserForm, LoginForm

from django.http import HttpResponse, HttpRequest, HttpResponseBadRequest, JsonResponse
from django.views.decorators.http import require_POST
import json

from django.db.models import Count

from .models import Quiz, Question, Answer, SurveyAnswer, SurveySubmission

from django.core.paginator import Paginator

from django.contrib.auth.models import auth

from django.contrib.auth import authenticate, login, logout

from typing import Optional

from .project_gen import generate_project

from django.urls import reverse

ALLOWED_INTERESTS = {
    "basketball","music","coding","cooking","gaming",
    "movies","reading","biology","soccer","painting",
    "astronomy","stock-market","geology","creative-writing","math",
    "football","business","cars","cyber-security","data-analysis",
    "social-media","hardware","drama","weight-lifting","travel",
}

def save_interests(request):

    if request.method != "POST":
        return HttpResponseBadRequest("Invalid")

    submission_id = request.session.get("submission_id")

    if not submission_id:
        return HttpResponseBadRequest("No Active Submission")

    submission = SurveySubmission.objects.get(id= submission_id)

    picked = request.POST.getlist("interests[]")

    if not picked:
        csv = request.POST.get("interests_csv", "")

        picked = [p for p in csv.split(",") if p]

    picked = [p for p in picked if p in ALLOWED_INTERESTS][:5]

    if not picked:
        return render(request, "app/interests.html", {"error": "Please pick at least one interest."})

    submission.set_interests(picked)

    return get_finish(request)



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
                        request, 'app/quiz.html', context={'topics': topics}
                    )
                    
                
                else:
                    return render(
                        request, 'app/index.html'
                    )

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

            return get_interests(request)


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

    submitted_answer_id = request.POST['answer_id']
    submitted_answer = Answer.objects.select_related('question', 'question__quiz').get(
        id=submitted_answer_id
    )

    current_question = submitted_answer.question
    quiz = current_question.quiz

    submission_id = request.session.get('submission_id')
    if submission_id is None:
        
        submission = SurveySubmission.objects.create(
            user=request.user if request.user.is_authenticated else None,
            quiz=quiz,
        )
        request.session['submission_id'] = submission.id
    else:
        submission = SurveySubmission.objects.get(id=submission_id)

    SurveyAnswer.objects.create(
        submission=submission,
        question=current_question,
        answer=submitted_answer,
    )

    return get_questions(request, is_start=False)

def get_finish(request) -> HttpResponse:
    
    quiz_id = request.session.get('quiz_id')

    if quiz_id:
        questions_count = Question.objects.filter(quiz_id=quiz_id).count()
    else:
        questions_count = 0

    responses = request.session.get('responses', [])
    responses_count = len(responses)


    request = _reset_quiz(request)

    return rec_view(request)

def _reset_quiz(request) -> HttpRequest:


    if 'question_id' in request.session:
        del request.session['question_id']

    if 'score' in request.session:
        del request.session['score']

    return request

def dashboard(request):
    return rec_view(request)


def user_logout(request):

    auth.logout(request)

    return redirect("")

def go_to_register(request):

    return redirect("register")

def get_interests(request):
    return render(request, 'app/interests.html')

def index(request):
    chosen = request.session.get("chosen_project")
    return render(request, "app/index.html", {"chosen": chosen})


def rec_view(request):
    projects = request.session.get("saved_projects")

    if not projects:
        projects = generate_project.get_project_recs(request.user)
        request.session["saved_projects"] = projects

    return render(request, "app/dashboard.html", {"projects": projects})

@require_POST
def save_chosen_project(request):
    
    index = None

    try:

        payload = json.loads(request.body.decode() or "{}")
        if isinstance(payload, dict):
            index = int(payload.get("index", None))

    except Exception:
        index = None


    if index is None:
        try:
            index = int(request.POST.get("index", None))

        except Exception:
            return HttpResponseBadRequest("Invalid Payload")

    projects = request.session.get("saved_projects")

    if not projects:

        projects = generate_project.get_project_recs(request.user)

    if (
        not isinstance(projects, list) or
        index is None or
        index < 0 or 
        index >= len(projects)
    ):
        return HttpResponseBadRequest("Invalid Index")

    chosen_project = projects[index]

    request.session["chosen_project"] = chosen_project

    if request.user.is_authenticated:
        from .models import UserProject

        try:
            UserProject.objects.create(
                user= request.user,
                project= chosen_project
            )
        except Exception:
            pass
    return JsonResponse({
        "success": True,
        "redirect_url": reverse("index")
    })    

