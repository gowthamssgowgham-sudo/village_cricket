from django.urls import path
from django.contrib.auth import views as auth_views
from . import views


urlpatterns = [
    # Public URLs
    path('', views.home_view, name='home'),
    path('teams/', views.team_list_view, name='teams'),
    path('register/', views.register_team_view, name='register_team'),
    path('fixtures/', views.fixtures_view, name='fixtures'),
    path('results/', views.results_view, name='results'),
    path('standings/', views.standings_view, name='standings'),

    # Admin / Auth
    path('login/', auth_views.LoginView.as_view(template_name='tournament/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # Organizer Portal
    path('organizer/dashboard/', views.admin_dashboard_view, name='admin_dashboard'),
    path('organizer/teams/', views.admin_teams_view, name='admin_teams'),
    path('organizer/teams/<int:team_id>/<slug:action>/', views.approve_team_view, name='approve_team'),
    path('organizer/teams/<int:team_id>/delete/', views.delete_team_view, name='delete_team'),
    path('organizer/schedule/', views.admin_schedule_view, name='admin_schedule'),
    path('organizer/match/<int:match_id>/update/', views.admin_update_match_view, name='admin_update_match'),
    path('organizer/settings/', views.admin_settings_view, name='admin_settings'),
    path('organizer/reset-tournament/', views.reset_tournament_view, name='reset_tournament'),
]