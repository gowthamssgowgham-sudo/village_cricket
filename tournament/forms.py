from django import forms
from .models import Match, Team, TournamentSetting


class TeamRegistrationForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ['name', 'captain_name', 'phone_number', 'player_list']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full p-3 border rounded-lg text-base', 'placeholder': 'Village Tigers'}),
            'captain_name': forms.TextInput(attrs={'class': 'w-full p-3 border rounded-lg text-base', 'placeholder': 'Ramesh Kumar'}),
            'phone_number': forms.TextInput(attrs={'class': 'w-full p-3 border rounded-lg text-base', 'placeholder': '+91 9876543210', 'type': 'tel'}),
            'player_list': forms.Textarea(attrs={'class': 'w-full p-3 border rounded-lg text-base', 'rows': 4, 'placeholder': 'Player 1, Player 2, Player 3...'}),
        }

    def clean_player_list(self):
        player_list = self.cleaned_data.get('player_list', '')
        players = [p.strip() for p in player_list.split(',') if p.strip()]
        
        if len(players) < 11 or len(players) > 15:
            raise forms.ValidationError(f"Please provide between 11 and 15 player names. You entered {len(players)}.")
            
        return player_list


class MatchForm(forms.ModelForm):
    class Meta:
        model = Match
        fields = ['team_a', 'team_b', 'date_time', 'venue', 'status']
        widgets = {
            'team_a': forms.Select(attrs={'class': 'w-full p-2.5 border rounded-lg text-sm'}),
            'team_b': forms.Select(attrs={'class': 'w-full p-2.5 border rounded-lg text-sm'}),
            'date_time': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'w-full p-2.5 border rounded-lg text-sm'}),
            'venue': forms.TextInput(attrs={'class': 'w-full p-2.5 border rounded-lg text-sm'}),
            'status': forms.Select(attrs={'class': 'w-full p-2.5 border rounded-lg text-sm'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Restrict choices to approved teams only
        approved_teams = Team.objects.filter(status='APPROVED')
        self.fields['team_a'].queryset = approved_teams
        self.fields['team_b'].queryset = approved_teams

    def clean(self):
        cleaned_data = super().clean()
        team_a = cleaned_data.get('team_a')
        team_b = cleaned_data.get('team_b')

        if team_a and team_b and team_a == team_b:
            raise forms.ValidationError("Team A and Team B cannot be the same team.")

        return cleaned_data


class MatchResultForm(forms.ModelForm):
    class Meta:
        model = Match
        fields = ['status', 'team_a_score', 'team_b_score', 'winner', 'margin_of_victory', 'man_of_the_match']
        widgets = {
            'status': forms.Select(attrs={'class': 'w-full p-2 border rounded'}),
            'team_a_score': forms.TextInput(attrs={'class': 'w-full p-2 border rounded', 'placeholder': '120/4 (10.0 ov)'}),
            'team_b_score': forms.TextInput(attrs={'class': 'w-full p-2 border rounded', 'placeholder': '115/8 (10.0 ov)'}),
            'winner': forms.Select(attrs={'class': 'w-full p-2 border rounded'}),
            'margin_of_victory': forms.TextInput(attrs={'class': 'w-full p-2 border rounded', 'placeholder': 'Won by 5 runs'}),
            'man_of_the_match': forms.TextInput(attrs={'class': 'w-full p-2 border rounded', 'placeholder': 'Ramesh Kumar'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            # Dynamically restrict winner choices to team_a, team_b, or None
            self.fields['winner'].queryset = Team.objects.filter(
                id__in=[self.instance.team_a.id, self.instance.team_b.id]
            )


class TournamentSettingForm(forms.ModelForm):
    class Meta:
        model = TournamentSetting
        fields = [
            'title', 'start_date', 'end_date', 'location', 
            'first_prize', 'second_prize', 'third_prize', 
            'contact_phone_1', 'contact_phone_2', 'full_address', 
            'announcement'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full p-2.5 border rounded-lg text-sm'}),
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'w-full p-2.5 border rounded-lg text-sm'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'w-full p-2.5 border rounded-lg text-sm'}),
            'location': forms.TextInput(attrs={'class': 'w-full p-2.5 border rounded-lg text-sm'}),
            'first_prize': forms.TextInput(attrs={'class': 'w-full p-2.5 border rounded-lg text-sm'}),
            'second_prize': forms.TextInput(attrs={'class': 'w-full p-2.5 border rounded-lg text-sm'}),
            'third_prize': forms.TextInput(attrs={'class': 'w-full p-2.5 border rounded-lg text-sm'}),
            'contact_phone_1': forms.TextInput(attrs={'class': 'w-full p-2.5 border rounded-lg text-sm', 'placeholder': '+91 98765 43210'}),
            'contact_phone_2': forms.TextInput(attrs={'class': 'w-full p-2.5 border rounded-lg text-sm', 'placeholder': '+91 91234 56789'}),
            'full_address': forms.Textarea(attrs={'class': 'w-full p-2.5 border rounded-lg text-sm', 'rows': 2}),
            'announcement': forms.Textarea(attrs={'class': 'w-full p-2.5 border rounded-lg text-sm', 'rows': 2}),
        }