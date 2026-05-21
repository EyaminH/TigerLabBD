from django.urls import path
from . import views 

urlpatterns = [
    path('', views.home, name='home'),
    path('challenges/', views.challenge_list, name='challenge_list'),
    path('challenges/<int:pk>/', views.challenge_detail, name='challenge_detail'),
    path('challenges/submit/', views.submit_challenge_user, name='submit_challenge'),
    path('challenges/<int:pk>/report/', views.report_challenge, name='report_challenge'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('review-challenges/', views.admin_review_list, name='admin_review'),
    path('review-challenges/<int:pk>/', views.admin_challenge_detail, name='admin_challenge_detail'),
    path('challenges/approve/<int:pk>/', views.approve_challenge, name='approve_challenge'),
    path('challenges/reject/<int:pk>/', views.reject_challenge, name='reject_challenge'),
    path('reports/resolve/<int:pk>/', views.resolve_report, name='resolve_report'),
]
