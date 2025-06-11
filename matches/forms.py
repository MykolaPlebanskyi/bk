from django import forms
from .models import Bet, Match, Map, Round, Team


# -------------------------------
# СТАВКИ
# -------------------------------

class BetForm(forms.ModelForm):
    class Meta:
        model = Bet
        fields = ['team', 'amount']


# -------------------------------
# АДМІН-ФОРМИ
# -------------------------------

class MatchAdminForm(forms.ModelForm):
    class Meta:
        model = Match
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['team_winner'].queryset = Team.objects.filter(
                id__in=[self.instance.team1_id, self.instance.team2_id]
            )


class MapAdminForm(forms.ModelForm):
    class Meta:
        model = Map
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            match = self.instance.match
            if match:
                self.fields['winner'].queryset = Team.objects.filter(
                    id__in=[match.team1_id, match.team2_id]
                )


class RoundAdminForm(forms.ModelForm):
    class Meta:
        model = Round
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            map_obj = self.instance.map
            if map_obj and map_obj.match:
                match = map_obj.match
                self.fields['winner'].queryset = Team.objects.filter(
                    id__in=[match.team1_id, match.team2_id]
                )
