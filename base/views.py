from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Group, Topic, Profile, Message, Exercise, Routine, ExerciseByPerson, Article, ArticleComment
from .forms import GroupForm, UserForm, ExerciseForm
from django.http import HttpResponse, JsonResponse
from django.core.exceptions import ObjectDoesNotExist
import datetime
import arrow
import calendar
from calendar import HTMLCalendar
from plotly import express as px
from plotly.offline import plot
import plotly.graph_objects as go

# Create your views here.

def loginView(request):
    mode = 'login'

    if request.user.is_authenticated:
        return redirect('home')
    #POST?
    if request.method == "POST":
        username = request.POST.get('username').lower()
        password = request.POST.get('password')

        try: #user exists?
            user = User.objects.get(username=username)
        except:
            #message error
            None
        
        user = authenticate(request, username=username, password=password) #create User

        if user is not None:
            login(request, user) #login
            return redirect('home')
        else:
            #message error
            None

    context = {'mode': mode}
    return render(request, 'base_templates/login_register.html', context)


@login_required(login_url='login-page')
def logoutView(request):
    logout(request)
    return redirect('home')


def registerView(request):
    mode = 'register'
    form = UserCreationForm()

    if request.method == 'POST':
        form = UserCreationForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()

            login(request, user)

            return redirect('home')
        else:
            None #error message

    return render(request, 'base_templates/login_register.html', {'form': form, 'mode': mode})            


def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ""

    groups = Group.objects.filter(
            Q(topic__name__icontains=q) |
            Q(name__icontains=q) |
            Q(description__contains=q)
    )

    topics = Topic.objects.all()[0:8]
    group_count = groups.count()
    topics_count = Topic.objects.count() - 8

    context = {'groups': groups, 'topics': topics, 'group_count': group_count, 'topics_count': topics_count}
    return render(request, 'base_templates/home.html', context)


@login_required(login_url='login-page')
def groupView(request, group_name):
    group = Group.objects.get(name=group_name)
    articles = Article.objects.filter(group=group)

    if request.method == 'POST':
        if 'join-group' in request.POST:
            group.participants.add(request.user)
        else:
            group.participants.remove(request.user)

    participants = group.participants.all()
    context = {'group': group, 'participants': participants, 'articles': articles}
    return render(request, 'base_templates/group_page.html', context)


@login_required(login_url='login-page')
def createGroup(request):
    mode = 'create'

    form = GroupForm()
    topics = Topic.objects.all()

    if request.method == "POST":
        try:
            existing_name = Group.objects.get(name=request.POST.get('name'))
            return HttpResponse('Already exists a group with that name')

        except ObjectDoesNotExist or ValueError:
            topic_name = request.POST.get('topic')
            topic, created =  Topic.objects.get_or_create(name=topic_name)

            Group.objects.create(
                host = request.user,
                topic = topic,
                name = request.POST.get('name'),
                description = request.POST.get('description'),
            )

            group = Group.objects.get(name=request.POST.get('name'))
            group.participants.add(request.user)

            return redirect('home')

    context = {'form': form, 'topics': topics, 'mode': mode}
    return render(request, 'base_templates/edit_page.html', context)


@login_required(login_url='login-page')
def editGroup(request, code):
    mode = 'edit'

    group = Group.objects.get(id=code)
    form = GroupForm(instance=group)
    topics = Topic.objects.all()

    if request.user != group.host:
        return redirect('home')

    if request.method == "POST":
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)

        group.topic = topic
        group.name = request.POST.get('name')
        group.description = request.POST.get('description')
        group.save()
        return redirect('home')
    
    context = {'form': form, 'group': group, 'topics': topics, 'mode': mode}
    return render(request, 'base_templates/edit_page.html', context)


@login_required(login_url='login-page')
def deleteGroup(request, code):
    group = Group.objects.get(id=code)

    if request.user != group.host:
        return redirect('home')

    if request.method == 'POST' and request.user.username == group.host.username:
        group.delete()
        return redirect('home')
    
    return render(request, 'base_templates/delete_group.html', {'group': group})

def profileView(request, code):
    context={}
    today = arrow.now().format('YYYY-MM-DD')
    exercises = ''
    went_to_gym = False

    try:
        user = User.objects.get(username=code)
        profile = Profile.objects.get(user=user)
        try:
            routine_day = Routine.objects.get(user=user, date=today)
            exercises = ExerciseByPerson.objects.filter(routine=routine_day)
            went_to_gym = True
        except:
            exercises = "Didnt went to gym yet"
            print('ay')

        context = {'profile': profile, 'exercises': exercises, 'went_to_gym': went_to_gym}
    except:
        return render(request, 'base_templates/profile_not_found.html', context)
    
    return render(request, 'base_templates/profile_view.html', context)

@login_required(login_url='login-page')
def editProfile(request, code):
    user = User.objects.get(username=code)
    profile = Profile.objects.get(user=user)

    if request.user != profile.user:
        return redirect('home')

    if request.method == "POST":
        profile.bio = request.POST.get('bio')
        profile.save()

        return redirect('profile-view', code=user.username)

    context={'profile': profile}
    return render(request, 'base_templates/edit_profile.html', context)


def groupMessages(request, group_name):
    group = Group.objects.get(name=group_name)
    messages = Message.objects.filter(group=group)

    datos = {
        "messages": {},
        "users": {},
    }

    for index, message in enumerate(messages, start=1):
        datos["messages"][index] = message.content
        datos["users"][index] = message.user.username

    return JsonResponse(datos)

    
def chatView(request, group_name):
    group = Group.objects.get(name=group_name)
    messages = Message.objects.filter(group=group)

    if request.method == "POST":
        message = request.POST.get('message')

        message_object = Message(content=message, user=request.user, group=group)
        message_object.save()

    context = {'group': group, 'messages': messages}
    return render(request, 'base_templates/group_chat.html', context)


def trackView(request, username):
    user = User.objects.get(username=username)
    exercises = Exercise.objects.all()
    today = arrow.now().format('YYYY-MM-DD')

    if request.method == 'POST':
        all_data = request.POST

        try:
            override_routine = Routine.objects.get(date=request.POST.get('date'), user=request.user).delete()
            print("overrided")
        except:
            None

        exercise_list = all_data.getlist('exercise')
        weight_list = all_data.getlist('weight')
        series_list = all_data.getlist('series')
        reps_list = all_data.getlist('reps')

        routine_today = Routine.objects.create(date=request.POST.get('date'), user=request.user, title=request.POST.get('title'))

        for exercise_not_object, weight, reps, series in zip(exercise_list, weight_list, reps_list, series_list):

            #function to capitalize the first letter
            split = exercise_not_object.split()
            words_to_join = []
            separator = ' '

            for word in split:
                words_to_join.append(word.capitalize())

            exercise_not_object = separator.join(words_to_join)

            exercise, created = Exercise.objects.get_or_create(name=exercise_not_object)
            ExerciseByPerson.objects.create(
                user=request.user,
                exercise=exercise,
                weight=weight,
                series=series,
                reps=reps,
                date=request.POST.get('date'),
                routine=routine_today
            )

        routine_today.save()

    context = {"exercises": exercises, "today": today} 
    return render(request, 'base_templates/track_page.html', context)

def calendarJson(request, username):
    routines = Routine.objects.filter(user=User.objects.get(username=username))
    routines_data = []

    for routine in routines:
        exercises = ExerciseByPerson.objects.filter(routine=routine)
        description = ""

        for exercise in exercises:
            description += f"{exercise.exercise.name} {exercise.series}x{exercise.reps}, {exercise.weight}kg. ++++"

        routines_data.append({
            'title': routine.title,
            'start': routine.date.strftime('%Y-%m-%d'),
            'description': description,
        })

    return JsonResponse(routines_data, safe=False)

def seeGymtrack(request, username):
    context = {} #js full calendar
    return render(request, 'base_templates/track_view.html', context)

def userGroups(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ""

    groups = Group.objects.filter(
            Q(topic__name__icontains=q),
            Q(participants=request.user)
    )

    topics = []

    for group in groups:
        if group.topic not in topics:
            topics.append(group.topic)

    group_count = len(groups)

    context = {'groups': groups, 'topics': topics, 'group_count': group_count}
    return render(request, 'base_templates/user_groups.html', context)

def graph(request):
    user = request.user

    #get exercises made by the user to send them to the datalist
    exercises_by_user = ExerciseByPerson.objects.filter(user=user)
    datalist_exercises = []
    for exercise_by_user in exercises_by_user:
        datalist_exercises.append(exercise_by_user.exercise.name)
    #end

    dates = []
    reps = []
    series = []
    weights = []

    if request.method == "POST":
        try:
            selected_exercise = Exercise.objects.get(name=request.POST.get('exercise-input'))
            exercises = ExerciseByPerson.objects.filter(exercise=selected_exercise, user=user)
        except:
            return HttpResponse('invalid exercise or you didn`t made it')
        
        if len(exercises) < 2:
            return HttpResponse('not enough exercises done')

        for exercise in exercises:
            dates.append(exercise.date)
            weights.append(exercise.weight)
            series.append(exercise.series)
            reps.append(exercise.reps)

        fig = go.Figure()

        fig.add_trace(go.Scatter(x=dates, y=weights, mode='lines', name='Weight'))
        fig.add_trace(go.Scatter(x=dates, y=series, mode='lines', name='Series'))
        fig.add_trace(go.Scatter(x=dates, y=reps, mode='lines', name='Reps'))

        title = selected_exercise.name + " Register"
        fig.update_layout(title=title, xaxis_title='Date', yaxis_title='Information')

        context = {'grafico': fig.to_html(), 'datalist_exercises': datalist_exercises}
        return render(request, 'base_templates/graph.html', context)
    
    context = {'datalist_exercises': datalist_exercises}
    return render(request, 'base_templates/graph.html', context)

def createArticle(request, group):
    if request.method == "POST":
        group_get = Group.objects.get(id=group)
        article_group = group_get
        user = request.user
        article_name = request.POST.get('article_name')
        article_content = request.POST.get('article_content')

        Article.objects.create(
            group = article_group,
            user = user,
            title = article_name,
            content = article_content
        )

    return render(request, "base_templates/create_article.html")

def viewArticle(request, article_id):
    article = Article.objects.get(id=article_id)

    article_group = article.group
    article_title = article.title
    article_content = article.content
    article_creator = article.user.username
    article_date = article.created

    if request.method == "POST":
        comment = request.POST.get('comment')

        ArticleComment.objects.create(
            article=article,
            user=request.user,
            content=comment
        )
    try:
        comments = ArticleComment.objects.all()[0:8]
    except:
        print("bad")

    context = {'comments': comments, 'title': article_title, 'content': article_content, 'creator': article_creator, 'date': article_date, 'group': article_group}

    return render(request, "base_templates/view_article.html", context)


