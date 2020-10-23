from django.utils.translation import gettext as _
from django.contrib import admin
from .models import Volunteer, Season, Section, Match, MatchVolunteeringRequest, VolunteeringRole


@admin.register(Volunteer)
class VolunteerAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'role', 'section', 'points')
    list_filter = ('role', 'section')


@admin.register(VolunteeringRole)
class VolunteeringRoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'reward', 'senior')
    list_filter = ('reward', 'senior')


def generate_requests(modeladmin, request, queryset):
    for match in queryset:
        match.generate_volunteering_requests()
generate_requests.short_description = _("Generate volunteering requests")


class MatchVolunteeringRequestInline(admin.TabularInline):
    model = MatchVolunteeringRequest


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ('competitor', 'section', 'starting_datetime', 'home')
    list_filter = ('section', 'starting_datetime', 'home')
    ordering = ('starting_datetime',)
    actions = [generate_requests]
    inlines = [MatchVolunteeringRequestInline, ]



admin.site.register(Season)
admin.site.register(Section)
admin.site.register(MatchVolunteeringRequest)

