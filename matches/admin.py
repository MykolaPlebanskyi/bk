from django.contrib import admin
from .models import Match, Team, Map, Round, Bet
from .forms import MatchAdminForm, MapAdminForm, RoundAdminForm


class RoundInline(admin.TabularInline):
    model = Round
    form = RoundAdminForm
    extra = 5
    fields = ('round_number', 'winner')
    ordering = ('round_number',)

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        match = obj.match if obj else None  # obj = Map instance

        class CustomFormset(formset):
            def __init__(self_inner, *args, **kwargs):
                super().__init__(*args, **kwargs)
                if match:
                    team_ids = [match.team1_id, match.team2_id]
                    for form in self_inner.forms:
                        form.fields['winner'].queryset = Team.objects.filter(id__in=team_ids)

        return CustomFormset



class MapInline(admin.StackedInline):
    model = Map
    form = MapAdminForm
    extra = 1
    fields = ('map_number', 'current', 'current_weapon', 'map_name', 'winner')


class MatchAdmin(admin.ModelAdmin):
    form = MatchAdminForm
    list_display = ('__str__', 'match_datetime', 'status', 'betting_open')
    inlines = [MapInline]


class MapAdmin(admin.ModelAdmin):
    form = MapAdminForm
    list_display = ('match', 'map_number', 'team1_score', 'team2_score')
    inlines = [RoundInline]


admin.site.register(Team)
admin.site.register(Match, MatchAdmin)
admin.site.register(Map, MapAdmin)
admin.site.register(Bet)
