from django.db import models
from django.core.exceptions import ValidationError


class TournamentSetting(models.Model):
    title = models.CharField(max_length=200, default="Village Premier League")
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    location = models.CharField(max_length=200, default="Village Central Ground")
    
    # Dynamic Prizes
    first_prize = models.CharField(max_length=100, default="₹25,000 + Trophy")
    second_prize = models.CharField(max_length=100, default="₹15,000 + Trophy")
    third_prize = models.CharField(max_length=100, default="₹5,000 + Trophy")
    
    # Contact Details
    contact_phone_1 = models.CharField(max_length=20, default="+91 98765 43210")
    contact_phone_2 = models.CharField(max_length=20, default="+91 91234 56789")
    full_address = models.TextField(default="Village Sports Complex, Near Gram Panchayat Office, District Central")

    announcement = models.TextField(blank=True, null=True, default="Tournament registrations are open!")

    def save(self, *args, **kwargs):
        # Enforce a single row in the database for global settings
        self.pk = 1
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Team(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending Approval'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    )

    name = models.CharField(max_length=100, unique=True)
    captain_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    player_list = models.TextField(help_text="Enter player names separated by commas (11-15 players)")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)

    def get_players_list(self):
        return [player.strip() for player in self.player_list.split(',') if player.strip()]

    def __str__(self):
        return f"{self.name} ({self.get_status_display()})"


class Match(models.Model):
    STATUS_CHOICES = (
        ('UPCOMING', 'Upcoming'),
        ('LIVE', 'Live'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    )

    team_a = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='matches_as_team_a')
    team_b = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='matches_as_team_b')
    
    winner = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True, related_name='matches_won')
    
    date_time = models.DateTimeField()
    venue = models.CharField(max_length=150, default="Main Village Ground")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='UPCOMING')
    
    # Results fields
    team_a_score = models.CharField(max_length=50, blank=True, null=True, help_text="e.g. 120/4 (10 overs)")
    team_b_score = models.CharField(max_length=50, blank=True, null=True, help_text="e.g. 115/8 (10 overs)")
    margin_of_victory = models.CharField(max_length=100, blank=True, null=True, help_text="e.g. Won by 5 runs")
    man_of_the_match = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        verbose_name_plural = "Matches"

    def clean(self):
        # Validate that team_a and team_b are distinct
        if self.team_a == self.team_b:
            raise ValidationError("Team A and Team B cannot be the same team.")
        
        # Validate that winner is one of the participating teams
        if self.winner and self.winner not in [self.team_a, self.team_b]:
            raise ValidationError("The winning team must be either Team A or Team B.")

    def __str__(self):
        return f"{self.team_a.name} vs {self.team_b.name} - {self.date_time.strftime('%d %b %H:%M')}"


class Standing(models.Model):
    team = models.OneToOneField(Team, on_delete=models.CASCADE)
    played = models.IntegerField(default=0)
    won = models.IntegerField(default=0)
    lost = models.IntegerField(default=0)
    tied = models.IntegerField(default=0)
    points = models.IntegerField(default=0)

    class Meta:
        ordering = ['-points', '-won']

    def __str__(self):
        return f"{self.team.name} - P: {self.played}, W: {self.won}, Pts: {self.points}"