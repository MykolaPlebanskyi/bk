# matches/models.py
from django.db import models
from accounts.models import CustomUser
from django.core.exceptions import ValidationError
from django.db.models import Count


class Team(models.Model):
    name = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='team_logos/')

    def __str__(self):
        return self.name


class Match(models.Model):
    STATUS_CHOICES = [
        ('live', 'Прямо зараз'),
        ('upcoming', 'Найближчий'),
        ('finished', 'Завершений'),
    ]
    team1 = models.ForeignKey(Team, related_name='team1_matches', on_delete=models.CASCADE)
    team2 = models.ForeignKey(Team, related_name='team2_matches', on_delete=models.CASCADE)
    team_winner = models.ForeignKey(Team, null=True, blank=True, on_delete=models.SET_NULL, related_name='won_matches',
                                    default=None)
    match_datetime = models.DateTimeField()
    location = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='upcoming')  # ← нове поле
    SERIES_CHOICES = [
        ('bo3', 'Best of 3'),
        ('bo5', 'Best of 5'),
    ]
    series_type = models.CharField(max_length=3, choices=SERIES_CHOICES, default='bo3')
    betting_open = models.BooleanField(default=True)  # ← Чи дозволено ставки
    team1_odds = models.FloatField(default=1.9)
    team2_odds = models.FloatField(default=1.9)

    def finalize_bets(self):
        if self.team_winner:
            for bet in self.bets.all():
                bet.is_won = (bet.team == self.team_winner)
                bet.calculate_profit()

    def save(self, *args, **kwargs):
        old_winner = None
        if self.pk:
            old_winner = Match.objects.filter(pk=self.pk).values_list('team_winner', flat=True).first()
        super().save(*args, **kwargs)
        if self.team_winner and self.team_winner_id != old_winner:
            self.finalize_bets()

    def get_final_score(self):
        # Рахуємо реально виграні карти
        team1_wins = self.maps.filter(winner=self.team1).count()
        team2_wins = self.maps.filter(winner=self.team2).count()

        # Якщо матч завершений, то рахунок відображаємо як є:
        if self.status == 'finished':
            return team1_wins, team2_wins

        # Якщо матч не завершений — показати прогрес (можливо йде гра)
        return team1_wins, team2_wins

    def __str__(self):
        return f"{self.team1.name} vs {self.team2.name} — {self.match_datetime.strftime('%Y-%m-%d %H:%M')}"


class Map(models.Model):
    match = models.ForeignKey(Match, related_name='maps', on_delete=models.CASCADE)
    map_number = models.PositiveIntegerField()
    map_name = models.CharField(max_length=100, blank=True, null=True)
    team1_score = models.PositiveIntegerField(default=0, editable=False)
    team2_score = models.PositiveIntegerField(default=0, editable=False)
    current = models.BooleanField(default=False)
    current_weapon = models.CharField(max_length=100, blank=True, null=True)
    winner = models.ForeignKey(Team, null=True, blank=True, on_delete=models.SET_NULL, related_name='won_maps',
                               default=None)

    def update_scores(self):
        team1_id = self.match.team1.id
        team2_id = self.match.team2.id

        self.team1_score = self.rounds.filter(winner_id=team1_id).count()
        self.team2_score = self.rounds.filter(winner_id=team2_id).count()

        if self.team1_score > self.team2_score:
            self.winner = self.match.team1
        elif self.team2_score > self.team1_score:
            self.winner = self.match.team2
        else:
            self.winner = None  # нічия або ще не визначено

        self.save()

    def __str__(self):
        return f"{self.match} — Map {self.map_number}"


class Bet(models.Model):
    match = models.ForeignKey(Match, related_name='bets', on_delete=models.CASCADE)
    user = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE, related_name='bet_history')
    amount = models.DecimalField(max_digits=10, decimal_places=1, default=0.0)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    odds_at_bet_time = models.DecimalField(max_digits=10, decimal_places=1, default=1.0)
    is_won = models.BooleanField(null=True, blank=True)
    profit = models.DecimalField(max_digits=10, decimal_places=0, default=0.0)

    def __str__(self):
        return f"{self.user.username} поставив {self.amount}₴ на {self.team.name}"

    def calculate_profit(self):
        if self.is_won is True:
            self.profit = self.amount * self.odds_at_bet_time
            self.user.balance = (self.user.balance or 0) + self.profit
            self.user.save(update_fields=['balance'])
        else:
            self.profit = 0.0
        self.save(update_fields=['profit', 'is_won'])

    @property
    def potential_profit(self):
        return self.amount * self.odds_at_bet_time


class Round(models.Model):
    map = models.ForeignKey(Map, related_name='rounds', on_delete=models.CASCADE)
    round_number = models.PositiveIntegerField()
    winner = models.ForeignKey(Team, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.map.update_scores()

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        self.map.update_scores()

    def clean(self):
        if self.winner not in [self.map.match.team1, self.map.match.team2]:
            raise ValidationError('Переможець повинен бути однією з команд матчу.')

    def __str__(self):
        return f"{self.map} — Раунд {self.round_number} (переможець: {self.winner})"
