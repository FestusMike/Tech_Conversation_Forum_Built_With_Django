from django.shortcuts import render, redirect, HttpResponse
from django.db.models import Q
from .models import Room, Topic, Message
from .models import User
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import MyUserCreationForm, UserUpdateForm
# Create your views here.


def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
)
    topics = Topic.objects.all()[0:5]
    room_count = len(rooms)
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))
    context = {'rooms': rooms, 'topics': topics, 'room_count' : room_count, 'room_messages' : room_messages}
    return render(request, 'main/home.html', context)

@login_required(login_url='login')
def room(request, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all().order_by('-created_at')
    participants = room.participants.all() 
    if request.method == 'POST':
        message = Message.objects.create(
            user = request.user,
            room=room,
            body = request.POST.get('body')
        )
        room.participants.add(request.user)
        return redirect('room', pk=room.id)
    context = {'room' : room, 'room_messages' : room_messages, 'participants': participants} 
    return render(request, 'main/room.html', context)

@login_required(login_url='login')
def CreateRoom(request):
    topics = Topic.objects.all()
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        Room.objects.create(
            host = request.user,
            topic = topic,
            name = request.POST.get('name'),
            description = request.POST.get('description')
        )
        return redirect('home')
    context = {'topics':topics}
    return render(request, 'main/create-room.html', context)

@login_required(login_url='login')
def UpdateRoom(request, pk):
    room = Room.objects.get(id=pk)
    topics = Topic.objects.all()
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()
        return redirect('home')
    context = {'topics':topics, 'room':room}
    return render(request, 'main/create-room.html', context)

@login_required(login_url='login')
def DeleteRoom(request, pk):
    room = Room.objects.get(id=pk)
    if request.method == 'POST':
        room.delete()
        return redirect('home')
    return render(request, 'main/delete.html', {'obj': room})

def LoginPage(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            user = User.objects.get(email=email)
        except:
            messages.error(request, 'User doesn\'t exist')
        user = authenticate(request, email=email, password=password)
        if user:
            login(request, user)
            messages.success(request, 'Login successful')
            return redirect('home')
            
        else:
            messages.error(request, 'Username or Password doesn\'t exist')
    return render(request, 'main/login.html') 

def Register(request):
    form = MyUserCreationForm()
    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            # user = form.save(commit=False)  #If you want to sterilize certain data before saving it finally into the db; maybe you want to convert an upper to a lower case       
            # user.username = user.username.lower()
            user = form.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'An Error occured')
    context = {'form' : form}
    return render(request, 'main/signup.html', context )

def LogoutUser(request):
    logout(request)
    return redirect('login')


login_required(login_url='login')
def DeleteMessage(request, pk):
    message = Message.objects.get(id=pk)    
    if request.method == 'POST':
        message.delete()
        return redirect('home')
    return render(request, 'main/delete.html', {'obj': message})


@login_required(login_url='login')
def UpdateMessage(request, pk):
    message = Message.objects.get(id=pk)
    if request.method == 'POST':
        form = request.POST.get('body', instance=message)
        if form.is_valid():
            form.save()
            return redirect('home')
    return render(request, 'main/room.html', {'message': message})


@login_required(login_url='login')
def UserProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    context={'user' : user, 'rooms':rooms, 'topics': topics, 'room_messages':room_messages}
    return render(request, 'main/profile.html', context)


@login_required(login_url='login')
def UpdateUser(request):
    user = request.user
    form = UserUpdateForm(instance=user)
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=user.id)
    context = {'form': form}
    return render(request, 'main/edit-user.html', context)

def TopicsPage(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    topics = Topic.objects.filter(name__icontains=q)
    return render(request, 'main/topics.html', {'topics': topics})