from django.contrib import admin
from .models import FamilyGroup, Member, Profile


@admin.register(FamilyGroup)
class FamilyGroupAdmin(admin.ModelAdmin):
    list_display = ("name", "owner")
    search_fields = ("name", "owner__username")


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ("name", "group", "relation", "mobile")
    list_filter = ("group",)
    search_fields = ("name", "mobile")


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "mobile")
