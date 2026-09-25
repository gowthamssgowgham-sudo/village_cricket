from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db import transaction
from .models import Team, Match, Standing, TournamentSetting
from .forms import TeamRegistrationForm, MatchForm, MatchResultForm, TournamentSettingForm


def recalculate_standings():
    """ Recalculates the points table dynamically based on finished matches """
    standings_map = {}
    
    # Reset or create table entries for all approved teams
    approved_teams = Team.objects.filter(status='APPROVED')
    for team in approved_teams:
        standing, _ = Standing.objects.get_or_create(team=team)
        standing.played = 0
        standing.won = 0
        standing.lost = 0
        standing.tied = 0
        standing.points = 0
        standings_map[team.id] = standing

    completed_matches = Match.objects.filter(status='COMPLETED')
    
    for match in completed_matches:
        t_a = match.team_a.id
        t_b = match.team_b.id

        if t_a in standings_map and t_b in standings_map:
            standings_map[t_a].played += 1
            standings_map[t_b].played += 1

            if match.winner:
                if match.winner.id == t_a:
                    standings_map[t_a].won += 1
                    standings_map[t_a].points += 2
                    standings_map[t_b].lost += 1
                elif match.winner.id == t_b:
                    standings_map[t_b].won += 1
                    standings_map[t_b].points += 2
                    standings_map[t_a].lost += 1
            else:
                # Tied / No result
                standings_map[t_a].tied += 1
                standings_map[t_b].tied += 1
                standings_map[t_a].points += 1
                standings_map[t_b].points += 1

    # Bulk update all standings records in a single database query
    if standings_map:
        Standing.objects.bulk_update(
            standings_map.values(), 
            ['played', 'won', 'lost', 'tied', 'points']
        )


# --- Public Views ---

def home_view(request):
    info = TournamentSetting.objects.first()
    live_matches = Match.objects.filter(status='LIVE')
    recent_results = Match.objects.filter(status='COMPLETED').order_by('-date_time')[:3]
    return render(request, 'tournament/home.html', {
        'info': info,
        'live_matches': live_matches,
        'recent_results': recent_results
    })


def team_list_view(request):
    teams = Team.objects.filter(status='APPROVED')
    return render(request, 'tournament/team_list.html', {'teams': teams})


def register_team_view(request):
    if request.method == 'POST':
        form = TeamRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your team application has been submitted! Waiting for Organizer approval.')
            return redirect('home')
    else:
        form = TeamRegistrationForm()
    return render(request, 'tournament/register_team.html', {'form': form})


def fixtures_view(request):
    fixtures = Match.objects.filter(status__in=['UPCOMING', 'LIVE']).order_by('date_time')
    return render(request, 'tournament/fixtures.html', {'fixtures': fixtures})


def results_view(request):
    results = Match.objects.filter(status='COMPLETED').order_by('-date_time')
    return render(request, 'tournament/results.html', {'results': results})


def standings_view(request):
    recalculate_standings()
    standings = Standing.objects.select_related('team').order_by('-points', '-won')
    return render(request, 'tournament/standings.html', {'standings': standings})


# --- Admin / Organizer Views ---

@login_required
def admin_dashboard_view(request):
    pending_teams_count = Team.objects.filter(status='PENDING').count()
    total_matches = Match.objects.count()
    completed_matches = Match.objects.filter(status='COMPLETED').count()
    return render(request, 'tournament/admin_dashboard.html', {
        'pending_teams_count': pending_teams_count,
        'total_matches': total_matches,
        'completed_matches': completed_matches,
    })


@login_required
def admin_teams_view(request):
    status_filter = request.GET.get('status', 'ALL')
    
    if status_filter in ['PENDING', 'APPROVED', 'REJECTED']:
        teams = Team.objects.filter(status=status_filter).order_by('-created_at')
    else:
        teams = Team.objects.all().order_by('-created_at')

    context = {
        'teams': teams,
        'current_filter': status_filter,
        'all_count': Team.objects.count(),
        'pending_count': Team.objects.filter(status='PENDING').count(),
        'approved_count': Team.objects.filter(status='APPROVED').count(),
        'rejected_count': Team.objects.filter(status='REJECTED').count(),
    }
    return render(request, 'tournament/admin_teams.html', context)


@login_required
def approve_team_view(request, team_id, action):
    team = get_object_or_404(Team, id=team_id)
    if action == 'approve':
        team.status = 'APPROVED'
        messages.success(request, f'Team {team.name} has been Approved.')
    elif action == 'reject':
        team.status = 'REJECTED'
        messages.warning(request, f'Team {team.name} has been Rejected.')
    team.save()
    recalculate_standings()
    return redirect('admin_teams')


@login_required
def delete_team_view(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    
    if request.method == 'POST':
        team_name = team.name
        team.delete()
        recalculate_standings()  # Recalculate standings after removing team/match history
        messages.success(request, f'Team "{team_name}" and all associated matches were permanently deleted.')
        return redirect('admin_teams')
        
    return redirect('admin_teams')


@login_required
def admin_schedule_view(request):
    if request.method == 'POST':
        form = MatchForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Match scheduled successfully!')
            return redirect('admin_schedule')
    else:
        form = MatchForm()
    
    matches = Match.objects.all().order_by('date_time')
    return render(request, 'tournament/admin_schedule.html', {'form': form, 'matches': matches})


@login_required
def admin_update_match_view(request, match_id):
    match = get_object_or_404(Match, id=match_id)
    if request.method == 'POST':
        form = MatchResultForm(request.POST, instance=match)
        if form.is_valid():
            form.save()
            recalculate_standings()
            messages.success(request, 'Match outcome updated successfully!')
            return redirect('admin_schedule')
    else:
        form = MatchResultForm(instance=match)
    return render(request, 'tournament/admin_update_match.html', {'form': form, 'match': match})


@login_required
def admin_settings_view(request):
    info, created = TournamentSetting.objects.get_or_create(id=1)
    if request.method == 'POST':
        form = TournamentSettingForm(request.POST, instance=info)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tournament details & prizes updated successfully!')
            return redirect('admin_settings')
    else:
        form = TournamentSettingForm(instance=info)
        
    return render(request, 'tournament/admin_settings.html', {'form': form})


@user_passes_test(lambda user: user.is_authenticated and user.is_staff, login_url='login')
def reset_tournament_view(request):
    if request.method == 'POST':
        with transaction.atomic():
            matches_deleted, _ = Match.objects.all().delete()
            standings_deleted, _ = Standing.objects.all().delete()
            teams_deleted, _ = Team.objects.all().delete()

        messages.success(
            request,
            f'Previous tournament data deleted: {teams_deleted} teams, '
            f'{matches_deleted} matches, and {standings_deleted} standings.',
        )
        return redirect('admin_dashboard')

    return render(request, 'tournament/admin_reset.html')