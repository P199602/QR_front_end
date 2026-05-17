from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import FamilyGroup, Member, Profile
from .serializers import ProfileSerializer
from .geo import apply_coords, coord_to_json, parse_coords
from .utils import create_qr


def _member_payload(member):
    return {
        "id": member.id,
        "group_id": member.group_id,
        "name": member.name,
        "father_name": member.father_name or "",
        "mobile": member.mobile or "",
        "relation": member.relation or "",
        "age": member.age,
        "location": member.location or "",
        "organization": member.organization or "",
        "place_visit": member.place_visit or "",
        "emergency_contact": member.emergency_contact or "",
        "latitude": coord_to_json(member.latitude),
        "longitude": coord_to_json(member.longitude),
        "photo": member.photo.url if member.photo else "",
        "qr": member.qr.url if member.qr else "",
        "qr_token": str(member.qr_token),
        "group_name": member.group.name,
    }


def _parse_age(value):
    if value in (None, ""):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _user_group(request, group_id):
    return get_object_or_404(FamilyGroup, id=group_id, owner=request.user)


def _user_member(request, member_id):
    return get_object_or_404(Member, id=member_id, group__owner=request.user)


def _apply_member_fields(member, data):
    if "name" in data:
        name = (data.get("name") or "").strip()
        if name:
            member.name = name

    for field in (
        "father_name",
        "mobile",
        "relation",
        "location",
        "organization",
        "place_visit",
        "emergency_contact",
    ):
        if field in data:
            setattr(member, field, data.get(field) or "")

    if "age" in data:
        member.age = _parse_age(data.get("age"))

    apply_coords(member, data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_group(request):
    name = (request.data.get("name") or "").strip()
    if not name:
        return Response({"error": "Group name is required."}, status=status.HTTP_400_BAD_REQUEST)

    group = FamilyGroup.objects.create(owner=request.user, name=name)
    return Response({"id": group.id, "name": group.name, "message": "Group created"}, status=status.HTTP_201_CREATED)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def groups(request):
    qs = FamilyGroup.objects.filter(owner=request.user).order_by("-id")
    data = [
        {
            "id": g.id,
            "name": g.name,
            "members": Member.objects.filter(group=g).count(),
        }
        for g in qs
    ]
    return Response(data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_member(request):
    group_id = request.data.get("group_id")
    name = (request.data.get("name") or "").strip()

    if not group_id or not name:
        return Response(
            {"error": "Group and member name are required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    group = _user_group(request, group_id)
    lat, lng = parse_coords(request.data)

    member = Member.objects.create(
        group=group,
        name=name,
        father_name=request.data.get("father_name") or "",
        mobile=request.data.get("mobile") or "",
        relation=request.data.get("relation") or "",
        age=_parse_age(request.data.get("age")),
        location=request.data.get("location") or "",
        organization=request.data.get("organization") or "",
        place_visit=request.data.get("place_visit") or "",
        emergency_contact=request.data.get("emergency_contact") or "",
        latitude=lat,
        longitude=lng,
    )

    if request.FILES.get("photo"):
        member.photo = request.FILES["photo"]
        member.save(update_fields=["photo"])

    create_qr(member)

    return Response(
        {"message": "Member added", "member": _member_payload(member)},
        status=status.HTTP_201_CREATED,
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def members(request):
    qs = Member.objects.filter(group__owner=request.user).select_related("group").order_by("-id")
    data = [
        {
            "id": m.id,
            "name": m.name,
            "relation": m.relation or "",
            "age": m.age,
            "group_name": m.group.name,
            "qr": m.qr.url if m.qr else "",
            "photo": m.photo.url if m.photo else "",
        }
        for m in qs
    ]
    return Response(data)


@api_view(["GET", "PUT", "DELETE"])
@permission_classes([IsAuthenticated])
def member_detail(request, id):
    member = _user_member(request, id)

    if request.method == "GET":
        return Response(_member_payload(member))

    if request.method == "DELETE":
        if member.photo:
            member.photo.delete(save=False)
        if member.qr:
            member.qr.delete(save=False)
        member.delete()
        return Response({"message": "Member deleted"}, status=status.HTTP_200_OK)

    name = (request.data.get("name") or member.name).strip()
    if not name:
        return Response({"error": "Name is required."}, status=status.HTTP_400_BAD_REQUEST)

    if request.data.get("group_id"):
        group = _user_group(request, request.data.get("group_id"))
        member.group = group

    _apply_member_fields(member, request.data)
    member.name = name

    if request.FILES.get("photo"):
        if member.photo:
            member.photo.delete(save=False)
        member.photo = request.FILES["photo"]

    member.save()

    return Response({"message": "Member updated", "member": _member_payload(member)})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def member_regenerate_qr(request, id):
    member = _user_member(request, id)

    if member.qr:
        member.qr.delete(save=False)

    create_qr(member)

    return Response(
        {"message": "QR code regenerated", "member": _member_payload(member)},
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])
@permission_classes([AllowAny])
def member_scan(request, token):
    member = get_object_or_404(Member, qr_token=token)
    return Response(_member_payload(member))


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def group_members(request, id):
    group = get_object_or_404(FamilyGroup, id=id, owner=request.user)
    member_qs = Member.objects.filter(group=group).order_by("name")
    data = [
        {
            "id": m.id,
            "name": m.name,
            "relation": m.relation or "",
            "age": m.age,
            "photo": m.photo.url if m.photo else "",
        }
        for m in member_qs
    ]
    return Response({"group": {"id": group.id, "name": group.name}, "members": data})


@api_view(["GET", "PUT"])
@permission_classes([IsAuthenticated])
def profile(request):
    profile_obj, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == "GET":
        return Response(ProfileSerializer(profile_obj).data)

    serializer = ProfileSerializer(profile_obj, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        apply_coords(profile_obj, request.data)
        profile_obj.save(update_fields=["latitude", "longitude"])
        return Response(ProfileSerializer(profile_obj).data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
