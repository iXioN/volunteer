import random
from django.db import models
from django.apps import apps
from django.utils.translation import gettext as _
from django.utils import timezone
from datetime import timedelta

from volunteers.constants import Role, Status


class SeasonManager(models.Manager):
    def current(self):
        now = timezone.now()
        current_year = now.year
        # last part of the season
        if now.month < 6:
            return self.all().get(start=current_year-1, stop=current_year)
        return self.all().get(start=current_year, stop=current_year+1)


class Season(models.Model):
    start = models.PositiveSmallIntegerField()
    stop = models.PositiveSmallIntegerField()

    objects = SeasonManager() # New default manager

    def __str__(self):
        return "{}/{}".format(self.start, self.stop)


class SectionManager(models.Manager):
    def volunteer_eligible(self):
        eligible_names = (
            '-19 F',
            '-19 M',
            'Senior F1',
            'Senior F2',
            'Senior M1',
            'Senior M2',
        )
        return self.all().filter(name__in=eligible_names)


class Section(models.Model):
    name = models.CharField(max_length=50)
    senior = models.BooleanField()
    objects = SectionManager() # New default manager

    def __str__(self):
        return self.name


class Volunteer(models.Model):
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    birthdate = models.DateField(null=True, blank=True, default=None)
    role = models.PositiveSmallIntegerField(choices=Role.CHOICES, null=True, blank=True, default=None)
    section = models.ForeignKey(Section, on_delete=models.CASCADE, null=True, blank=True, default=None)
    season = models.ForeignKey(Season, on_delete=models.CASCADE, null=True, blank=True, default=None)
    points = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return "{} {} ({})".format(self.first_name, self.last_name, self.section)


class Match(models.Model):
    competitor = models.CharField(max_length=200)
    season = models.ForeignKey(Season, on_delete=models.CASCADE)
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    starting_datetime = models.DateTimeField()
    home = models.BooleanField(default=True)

    def get_name(self):
        if self.home:
            return "THAC/{}".format(self.competitor)
        return "{}/THAC".format(self.competitor)

    def get_role_reqests_names(self):
        return self.matchvolunteeringrequest_set.all().order_by('role').values_list("role__name", flat=True)

    def get_role_reuqests(self):
        return self.matchvolunteeringrequest_set.all().order_by('role')

    def get_convocation_datetime(self):
        return self.starting_datetime - timedelta(hours=1)

    def __str__(self):
        return "{} {} {}".format(self.get_name(), self.section, self.starting_datetime)

    def generate_volunteering_requests(self):
        # Only generate request for home match
        if not self.home:
            return
        # get all volunteers eligible
        season = apps.get_model('volunteers', 'Season').objects.current()
        # get the eligible section and remove the match section
        eligible_section = apps.get_model('volunteers', 'Section').objects.volunteer_eligible().exclude(id=self.section.id)
        # TODO will need to remove all volunteeres with an already approved request for the same weekend

        volunteers_qs = apps.get_model('volunteers', 'Volunteer').objects.filter(
            season=season,
            section__in=eligible_section,
            role=Role.PLAYER
        )
        # order volunteers by points and get the number of VolunteeringRole (should be twice what we need)
        volunteers_qs = volunteers_qs.order_by('points')
        # get the maximum number of possible roles
        max_roles = apps.get_model('volunteers', 'VolunteeringRole').objects.all().count()
        volunteers = list(volunteers_qs[:max_roles])
        random.shuffle(volunteers)

        # Now generate the MatchVolunteeringRequest
        needed_roles_qs = apps.get_model('volunteers', 'VolunteeringRole').objects.filter(senior=self.section.senior)

        MatchVolunteeringRequest = apps.get_model('volunteers', 'MatchVolunteeringRequest')
        for index, role in enumerate(needed_roles_qs):
            MatchVolunteeringRequest.objects.create(
                section=self.section,
                volunteer=volunteers[index],
                role=role,
                match=self,
                status=Status.SENT,
            )

class VolunteeringRole(models.Model):
    name = models.CharField(max_length=200)
    reward = models.PositiveSmallIntegerField(default=1)
    senior = models.BooleanField()

    def __str__(self):
        cat = _("senior") if self.senior else _("young")
        return "{} {} ({} pts)".format(self.name, cat, self.reward)


class MatchVolunteeringRequest(models.Model):
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    volunteer = models.ForeignKey(Volunteer, on_delete=models.CASCADE)
    role = models.ForeignKey(VolunteeringRole, on_delete=models.CASCADE)
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    status = models.PositiveSmallIntegerField(choices=Status.CHOICES)
    creation_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{} {} {} ".format(self.volunteer, self.role, self.match)
