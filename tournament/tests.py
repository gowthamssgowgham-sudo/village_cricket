from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Match, Standing, Team, TournamentSetting


class TournamentResetViewTests(TestCase):
	def setUp(self):
		self.admin = get_user_model().objects.create_user(
			username='admin', password='test-password', is_staff=True
		)
		self.user = get_user_model().objects.create_user(
			username='user', password='test-password'
		)
		self.team_a = Team.objects.create(
			name='Team A', captain_name='Captain A', phone_number='1234567890',
			player_list=', '.join(f'Player {number}' for number in range(1, 12)),
		)
		self.team_b = Team.objects.create(
			name='Team B', captain_name='Captain B', phone_number='1234567891',
			player_list=', '.join(f'Player {number}' for number in range(1, 12)),
		)
		self.match = Match.objects.create(
			team_a=self.team_a,
			team_b=self.team_b,
			date_time=timezone.now(),
		)
		Standing.objects.create(team=self.team_a)
		TournamentSetting.objects.create(title='Keep this setting')

	def test_staff_can_reset_tournament_data(self):
		self.client.force_login(self.admin)

		response = self.client.post(reverse('reset_tournament'))

		self.assertEqual(response.status_code, 302)
		self.assertEqual(response['Location'], reverse('admin_dashboard'))
		self.assertEqual(Team.objects.count(), 0)
		self.assertEqual(Match.objects.count(), 0)
		self.assertEqual(Standing.objects.count(), 0)
		self.assertEqual(TournamentSetting.objects.get().title, 'Keep this setting')

	def test_non_staff_cannot_reset_tournament_data(self):
		self.client.force_login(self.user)

		response = self.client.post(reverse('reset_tournament'))

		self.assertEqual(response.status_code, 302)
		self.assertEqual(
			response['Location'],
			f'{reverse("login")}?next={reverse("reset_tournament")}',
		)
		self.assertTrue(Team.objects.filter(pk=self.team_a.pk).exists())
		self.assertTrue(Match.objects.filter(pk=self.match.pk).exists())
