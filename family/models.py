from django.db import models
from django.contrib.auth.models import User
import uuid


class FamilyGroup(models.Model):

    owner=models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    name=models.CharField(
        max_length=100
    )

    def __str__(self):
        return self.name


class Member(models.Model):

    group=models.ForeignKey(
        FamilyGroup,
        on_delete=models.CASCADE
    )

    name=models.CharField(
        max_length=100
    )

    father_name=models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    mobile=models.CharField(
        max_length=15,
        blank=True,
        null=True
    )

    relation=models.CharField(
        max_length=50,
        blank=True,
        null=True
    )

    age=models.IntegerField(
        blank=True,
        null=True
    )

    location=models.CharField(
        max_length=200,
        blank=True,
        null=True
    )

    organization=models.CharField(
        max_length=200,
        blank=True,
        null=True
    )

    place_visit=models.CharField(
        max_length=200,
        blank=True,
        null=True
    )

    emergency_contact=models.CharField(
        max_length=15,
        blank=True,
        null=True
    )

    latitude=models.DecimalField(
        max_digits=9,
        decimal_places=6,
        blank=True,
        null=True,
    )

    longitude=models.DecimalField(
        max_digits=9,
        decimal_places=6,
        blank=True,
        null=True,
    )

    photo=models.ImageField(
        upload_to='members/',
        blank=True,
        null=True
    )

    qr=models.ImageField(
        upload_to='qr/',
        blank=True,
        null=True
    )

    qr_token=models.UUIDField(
        default=uuid.uuid4,
        editable=False
    )

    def __str__(self):
        return self.name



class Profile(models.Model):

    user=models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='family_profile'
    )

    photo=models.ImageField(
        upload_to='profile/',
        null=True,
        blank=True
    )

    mobile=models.CharField(
        max_length=15,
        blank=True
    )

    latitude=models.DecimalField(
        max_digits=9,
        decimal_places=6,
        blank=True,
        null=True,
    )

    longitude=models.DecimalField(
        max_digits=9,
        decimal_places=6,
        blank=True,
        null=True,
    )

    def __str__(self):
        return self.user.username