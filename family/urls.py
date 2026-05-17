from django.urls import path
from . import views

urlpatterns = [
    path("group/", views.create_group),
    path("groups/", views.groups),
    path("add_member/", views.add_member),
    path("members/", views.members),
    path("member/<int:id>/", views.member_detail),
    path("member/<int:id>/regenerate-qr/", views.member_regenerate_qr),
    path("member/scan/<uuid:token>/", views.member_scan),
    path("group/<int:id>/members/", views.group_members),
    path("profile/", views.profile),
]
