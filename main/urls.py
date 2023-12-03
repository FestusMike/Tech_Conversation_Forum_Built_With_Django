from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.home, name='home'),
    path('room/<str:pk>/', views.room, name='room'),
    path('create/', views.CreateRoom, name='create-room'),
    path('update/<str:pk>/', views.UpdateRoom, name='update-room'),
    path('delete/<str:pk>/', views.DeleteRoom, name='delete-room'),
    path('delete-message/<str:pk>/', views.DeleteMessage, name='delete-message'),
    path('update-message/<str:pk>/', views.UpdateMessage, name='update-message'),
    path('user-profile/<str:pk>/', views.UserProfile, name='user-profile'),
    path('update-user/', views.UpdateUser, name='update-user'),
    path('topics/', views.TopicsPage, name='topics'),
    path('login/', views.LoginPage, name='login'),
    path('logout/', views.LogoutUser, name='logout'),
    path('register/', views.Register, name='register'),
    
]