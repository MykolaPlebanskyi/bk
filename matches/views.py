# matches/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.db.models import Sum, Count, Q
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Match, Team, Bet
from .forms import BetForm


def home_view(request):
    now = timezone.now()
    matchsets = {
        'upcoming': Match.objects.select_related('team1', 'team2').prefetch_related('maps__rounds').filter(
            status='upcoming'),
        'live': Match.objects.select_related('team1', 'team2').prefetch_related('maps__rounds').filter(status='live'),
        'past': Match.objects.select_related('team1', 'team2').prefetch_related('maps__rounds').filter(
            status='finished'),
    }

    for matchset in matchsets.values():
        for match in matchset:
            match.team1_map_wins, match.team2_map_wins = match.get_final_score()

            team1_rounds = 0
            team2_rounds = 0
            for m in match.maps.all():
                for r in m.rounds.all():
                    if r.winner_id == match.team1_id:
                        team1_rounds += 1
                    elif r.winner_id == match.team2_id:
                        team2_rounds += 1

            match.team1_rounds = team1_rounds
            match.team2_rounds = team2_rounds

    return render(request, 'matches/home.html', matchsets)


@login_required
def match_detail(request, match_id):
    match = get_object_or_404(Match, id=match_id)
    maps = match.maps.all().order_by('map_number')
    current_map = match.maps.filter(current=True).first()
    # odds_team1, odds_team2 = calculate_odds(match)
    odds_team1, odds_team2 = match.team1_odds, match.team2_odds
    user = request.user

    user_has_bet = Bet.objects.filter(match=match, user=user).exists()

    if request.method == "POST" and not user_has_bet:
        if not match.betting_open:
            messages.error(request, "Ставки на цей матч закриті.")
            return redirect('match_detail', match_id=match.id)

        form = BetForm(request.POST)
        form.fields['team'].queryset = Team.objects.filter(id__in=[match.team1.id, match.team2.id])

        if form.is_valid():
            amount = form.cleaned_data['amount']
            team = form.cleaned_data['team']

            if user.balance < amount:
                messages.error(request, "Недостатньо коштів для ставки.")
            else:
                user.balance -= amount
                user.save()

                odds = match.team1_odds if team == match.team1 else match.team2_odds

                Bet.objects.create(
                    match=match,
                    user=user,
                    amount=amount,
                    team=team,
                    odds_at_bet_time=odds
                )

                messages.success(request, f"Ставка на {team.name} успішно зроблена!")
                return redirect('match_detail', match_id=match.id)
    else:
        form = BetForm()
        form.fields['team'].queryset = Team.objects.filter(id__in=[match.team1.id, match.team2.id])

    return render(request, 'matches/match_detail.html', {
        'match': match,
        'maps': maps,
        'current_map': current_map,
        'odds_team1': odds_team1,
        'odds_team2': odds_team2,
        'form': form,
        'user_has_bet': user_has_bet,
    })
