from distutils.util import strtobool
from django.conf import settings
from django.db import models
from django.contrib.auth import get_user_model

class Organization(models.Model):
    slug = models.SlugField(max_length=16, blank=False, unique=True)
    name = models.CharField(max_length=64, blank=True)
    description = models.TextField(blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    contact = models.JSONField(blank=True, default=dict)

    owner = models.ForeignKey(get_user_model(), null=True,
        blank=True, on_delete=models.SET_NULL, related_name='+')

    def __str__(self):
        return self.slug
    class Meta:
        default_permissions = ()

class Membership(models.Model):
    WORKER = 'worker'
    SUPERVISOR = 'supervisor'
    MAINTAINER = 'maintainer'
    OWNER = 'owner'

    user = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL,
        null=True, related_name='+')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE,
        related_name='members')
    is_active = models.BooleanField(default=False)
    joined_date = models.DateTimeField(null=True)
    role = models.CharField(max_length=16, choices=[
        (WORKER, 'Worker'),
        (SUPERVISOR, 'Supervisor'),
        (MAINTAINER, 'Maintainer'),
        (OWNER, 'Owner'),
    ])

    class Meta:
        default_permissions = ()
        unique_together = ('user', 'organization')


# Inspried by https://github.com/bee-keeper/django-invitations
class Invitation(models.Model):
    key = models.CharField(max_length=64, primary_key=True)
    accepted = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(get_user_model(), null=True, on_delete=models.SET_NULL)
    membership = models.OneToOneField(Membership, on_delete=models.CASCADE)

    def send(self):
        if not strtobool(settings.ORG_INVITATION_CONFIRM):
            self.membership.is_active = True
            self.membership.joined_date = self.created_date
            self.membership.save()

        # TODO: use email backend to send invitations as well

    class Meta:
        default_permissions = ()
