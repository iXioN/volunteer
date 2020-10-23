from django.utils.translation import gettext as _


class Role(object):
    PLAYER = 1
    ADMINISTRATOR = 2
    CHOICES = [
        (PLAYER, _("Player")),
        (ADMINISTRATOR, _('Admin')),
    ]


class Status(object):
    SENT = 1
    ACCEPTED = 2
    REJECTED = 3
    CANCELLED = 4
    CHOICES = [
        (SENT, _('Sent')),
        (ACCEPTED, _('Accepted')),
        (REJECTED, _('Rejected')),
        (CANCELLED, _('Cancelled')),
    ]
