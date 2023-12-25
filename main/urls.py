from django.urls import path
from . import views



urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('home/', views.HomeView.as_view(), name='home'),
    path('room/<str:pk>/', views.RoomView.as_view(), name='room'),
    
    path('create/', views.CreateRoomView.as_view(), name='create-room'),
    path('update/<str:pk>/', views.UpdateRoomView.as_view(), name='update-room'),
    path('delete/<str:pk>/', views.DeleteRoomView.as_view(), name='delete-room'),
    
    path('delete-message/<str:pk>/',views.DeleteMessageView.as_view(), name='delete-message'),
    
    path('user-profile/<str:pk>/', views.UserProfileView.as_view(), name='user-profile'),
    path('update-user/', views.UpdateUserView.as_view(), name='update-user'),
    path('topics/', views.TopicsPageView.as_view(), name='topics'),
    
    path('login/', views.LoginPageView.as_view(), name='login'),
    path('logout/', views.LogoutUserView.as_view(), name='logout'),
    path('register/', views.RegisterView.as_view(), name='register'),
    
]


