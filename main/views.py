from django.shortcuts import render, redirect
from django.db.models import Q
from .models import Room, Topic, Message
from .models import User
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import MyUserCreationForm, UserUpdateForm
from django.views import View
from django.utils.decorators import method_decorator
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
import os

# Create your views here.

class HomeView(View):
    template_name = 'main/home.html'

    def get(self, request, *args, **kwargs):
        q = request.GET.get('q', '')
        rooms = Room.objects.filter(
            Q(topic__name__icontains=q) |
            Q(name__icontains=q) |
            Q(description__icontains=q)
        )
        topics = Topic.objects.all()[0:5]
        room_count = len(rooms)
        room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))
        context = {'rooms': rooms, 'topics': topics, 'room_count': room_count, 'room_messages': room_messages}
        return render(request, self.template_name, context)


class RoomView(View):
    template_name = 'main/room.html'

    @method_decorator(login_required(login_url='login'))
    def get(self, request, pk, *args, **kwargs):
        room = Room.objects.get(id=pk)
        room_messages = room.message_set.all().order_by('-created_at')
        participants = room.participants.all()
        context = {'room': room, 'room_messages': room_messages, 'participants': participants}
        return render(request, self.template_name, context)

    @method_decorator(login_required(login_url='login'))
    def post(self, request, pk, *args, **kwargs):
        room = Room.objects.get(id=pk)
        message = Message.objects.create(
            user=request.user,
            room=room,
            body=request.POST.get('body')
        )
        room.participants.add(request.user)
        return redirect('room', pk=room.id)


class CreateRoomView(View):
    template_name = 'main/create-room.html'

    @method_decorator(login_required(login_url='login'))
    def get(self, request, *args, **kwargs):
        topics = Topic.objects.all()
        context = {'topics': topics}
        return render(request, self.template_name, context)

    @method_decorator(login_required(login_url='login'))
    def post(self, request, *args, **kwargs):
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description')
        )
        return redirect('home')


class UpdateRoomView(View):
    template_name = 'main/create-room.html'

    @method_decorator(login_required(login_url='login'))
    def get(self, request, pk, *args, **kwargs):
        room = Room.objects.get(id=pk)
        topics = Topic.objects.all()
        context = {'topics': topics, 'room': room}
        return render(request, self.template_name, context)

    @method_decorator(login_required(login_url='login'))
    def post(self, request, pk, *args, **kwargs):
        room = Room.objects.get(id=pk)
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()
        return redirect('home')


class DeleteRoomView(View):
    template_name = 'main/delete.html'

    @method_decorator(login_required(login_url='login'))
    def get(self, request, pk, *args, **kwargs):
        room = Room.objects.get(id=pk)
        return render(request, self.template_name, {'obj': room})

    @method_decorator(login_required(login_url='login'))
    def post(self, request, pk, *args, **kwargs):
        room = Room.objects.get(id=pk)
        room.delete()
        return redirect('home')


class LoginPageView(View):
    template_name = 'main/login.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')

        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, 'User doesn\'t exist')
            return render(request, self.template_name)

        user = authenticate(request, email=email, password=password)

        if user:
            login(request, user)
            messages.success(request, 'Login successful')
            return redirect('home')
        else:
            messages.error(request, 'Email and Password don\'t match ')

        return render(request, self.template_name)


class RegisterView(View):
    template_name = 'main/signup.html'

    def get(self, request, *args, **kwargs):
        form = MyUserCreationForm()
        context = {'form': form}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = MyUserCreationForm(request.POST)
        
        if form.is_valid():
            user = form.save()
 
            # Authenticate the user using the default authentication backend
            auth_user = authenticate(request, username=user.username, password=form.cleaned_data['password1'])
            
            if auth_user:
                login(request, auth_user)

                # Call Sendinblue API to send a transactional email
                try:
                    # Set up Sendinblue API configuration
                    configuration = sib_api_v3_sdk.Configuration()
                    configuration.api_key['api-key'] = os.environ.get('EMAIL_API_KEY')

                    # Create an instance of the Sendinblue TransactionalEmailsApi
                    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))

                    # Define email parameters
                    subject = "Welcome to TalkingTech!"
                    sender = {"name" : 'TalkingTech', "email": os.environ.get('EMAIL_SENDER')}
                    reply_to = {"email": os.environ.get('EMAIL_REPLY_TO')}
                    html_content = f"<html><body><h1>Welcome, {user.username}!</h1> <p>We are happy to have you here</p></body></html>"
                    to = [{"email": user.email, "name": user.username}]

                    # Create an instance of SendSmtpEmail
                    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(to=to, reply_to=reply_to, html_content=html_content, sender=sender, subject=subject)

                    # Send the transactional email
                    api_response = api_instance.send_transac_email(send_smtp_email)
                    print(api_response)

                except ApiException as e:
                    print("Exception when calling SMTPApi->send_transac_email: %s\n" % e)

                return redirect('home')

            else:
                messages.error(request, 'Failed to authenticate the user')
        else:
            messages.error(request, 'An error occurred')

        context = {'form': form}
        return render(request, self.template_name, context)



class LogoutUserView(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect('home')


class DeleteMessageView(View):
    template_name = 'main/delete.html'

    @method_decorator(login_required(login_url='login'))
    def get(self, request, pk, *args, **kwargs):
        message = Message.objects.get(id=pk)
        return render(request, self.template_name, {'obj': message})

    @method_decorator(login_required(login_url='login'))
    def post(self, request, pk, *args, **kwargs):
        message = Message.objects.get(id=pk)
        message.delete()
        return redirect('home')


class UserProfileView(View):
    template_name = 'main/profile.html'

    @method_decorator(login_required(login_url='login'))
    def get(self, request, pk, *args, **kwargs):
        user = User.objects.get(id=pk)
        rooms = user.room_set.all()
        room_messages = user.message_set.all()
        topics = Topic.objects.all()
        context = {'user': user, 'rooms': rooms, 'topics': topics, 'room_messages': room_messages}
        return render(request, self.template_name, context)


class UpdateUserView(View):
    template_name = 'main/edit-user.html'

    @method_decorator(login_required(login_url='login'))
    def get(self, request, *args, **kwargs):
        user = request.user
        form = UserUpdateForm(instance=user)
        context = {'form': form}
        return render(request, self.template_name, context)

    @method_decorator(login_required(login_url='login'))
    def post(self, request, *args, **kwargs):
        user = request.user
        form = UserUpdateForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=user.id)
        context = {'form': form}
        return render(request, self.template_name, context)


class TopicsPageView(View):
    template_name = 'main/topics.html'

    def get(self, request, *args, **kwargs):
        q = request.GET.get('q', '')
        topics = Topic.objects.filter(name__icontains=q)
        return render(request, self.template_name, {'topics': topics})




