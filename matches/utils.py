from django.db.models import Sum
def calculate_odds(match):
    total_bets = match.bets.aggregate(total=Sum('amount'))['total'] or 0
    team1_bets = match.bets.filter(team=match.team1).aggregate(total=Sum('amount'))['total'] or 0
    team2_bets = match.bets.filter(team=match.team2).aggregate(total=Sum('amount'))['total'] or 0

    def safe_odds(team_bet):
        if team_bet == 0:
            return 2.0  # або фіксоване значення
        return round(total_bets / team_bet, 2)

    return safe_odds(team1_bets), safe_odds(team2_bets)