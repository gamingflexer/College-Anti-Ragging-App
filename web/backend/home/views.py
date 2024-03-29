from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import RegisterUserForm
from api.views import dashboard_data_main
from api.location import find_nearest
from datetime import datetime
from home.utils import location_finder
import time

def index(request):
    return render(request, 'index.html', {})

@login_required(login_url='/login/')
def dashboard(request):
    if request.user.is_authenticated:
        username_admin = str(request.user)
        data1 = dashboard_data_main()
        result = sorted(data1,key=lambda x : datetime.strptime(x['time'][:-9],'%Y-%m-%d %H:%M:%S.%f'))[-7:]
        for i in range(len(result)):
            result[i]['time'] = result[i]['time'][:10]
            result[i]['location'] = location_finder(result[i]['lat'],result[i]['lng'])
        data = {"total":len(data1),"last_updated": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}
        result.reverse()
        return render(request, 'dashboard.html', {'data':data,'data1':result})

@login_required(login_url='/login/')
def profile(request):
    if request.user.is_authenticated:
        return render(request, 'profile.html', )

@login_required(login_url='/login/')
def maps(request,uid):
    if request.user.is_authenticated:
        if uid != '1':
            data = dashboard_data_main(only_firebase=True)
            context = {}
            user_data = []
            for user in data:
                if user['uid'] == uid:
                    user_data.append(user)
            result = sorted(user_data,key=lambda x : datetime.strptime(x['time'][:-9],'%Y-%m-%d %H:%M:%S.%f'))[-1]
            context['lat'] = result['lat']
            context['lng'] = result['lng']
            context['description'] = " ".join([result['uid'],f"{result['time'][:10]}"])
            context["cords_nearset"] = find_nearest(context['lat'],context['lng'])
            return render(request, 'map.html', {'data':context})
        else:
            return render(request, 'map.html', {})

def page_404(request):
    return render(request, 'page_404.html', {})

@login_required(login_url='/login/')
def user_info(request,file_id):
    print(file_id)
    return render(request, 'resume.html', {})

def login_user(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        if request.method == "POST":
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                messages.success(request, ("There Was An Error Logging In, Try Again..."))	
                return redirect('login')	

        else:
            return render(request, 'login.html', {})

def logout_user(request):
    logout(request)
    messages.success(request, ("You Were Logged Out!"))
    return redirect('index')


def register_user(request):
    #print(request.user.is_authenticated())
    if request.user.is_authenticated:
        return redirect('home')
    else:
        if request.method == "POST":
            form = RegisterUserForm(request.POST)
            context ={}
            context['form']= form
            if form.is_valid():
                form.save()
                username = form.cleaned_data['username']
                password = form.cleaned_data['password1']
                user = authenticate(username=username, password=password)
                login(request, user)
                messages.success(request, ("Registration Successful!"))
                return redirect('home')
        else:
            form = RegisterUserForm()

        return render(request, 'auth/register_user.html', {
            'form':form,
            })