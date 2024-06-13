from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),
    path('group/<str:group_name>/', views.groupView, name='group'),
    path('create-group/', views.createGroup, name='create-group'),
    path('group/edit/<str:code>/', views.editGroup, name='editgroup-page'),
    path('group/delete/<str:code>/', views.deleteGroup, name='deletegroup-page'),
    path('login/', views.loginView, name='login-page'),
    path('register/', views.registerView, name='register-page'),
    path('logout/', views.logoutView, name='logout-page'),
    path('profile/<str:code>', views.profileView, name='profile-view'),
    path('profile/edit/<str:code>', views.editProfile, name='profile-edit'),
    path('profile/usernotfound', views.profileView, name='profile-not-found'),
    path('ajax/mensajes/<str:group_name>', views.groupMessages),
    path('group/chat/<str:group_name>', views.chatView, name='group-chat'),
    path('profile/gymtrack/<str:username>', views.trackView, name='track-page'),
    path('profile/gymtrack/view/<str:username>', views.seeGymtrack, name='track-view'),
    path('json/calendardata/<str:username>', views.calendarJson, name='calendar-json'),
    path('mygroups/', views.userGroups, name='user-groups'),
    path('graph/', views.graph, name='graph'),
    path('create-article/<str:group>', views.createArticle, name='create-article'),
    path('article/<str:article_id>', views.viewArticle, name='view-article'),
]
