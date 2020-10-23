from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.apps import apps
from django.utils import timezone
from datetime import timedelta

# Create your views here.
from django.http import HttpResponse


@login_required
def index(request):
    season = apps.get_model('volunteers', 'Season').objects.current()
    now = timezone.now()
    # get future match
    match_qs = apps.get_model('volunteers', 'Match').objects.filter(
        season=season,
        starting_datetime__gte=now - timedelta(days=1) # Yesyerday, to be sure to show the match of the weekend
    ).order_by('starting_datetime', 'section')

    context = {"matchs": match_qs}
    return render(request, 'summary.html', context)
