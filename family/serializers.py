from rest_framework import serializers
from .models import FamilyGroup, Member, Profile


class GroupSerializer(serializers.ModelSerializer):
    members = serializers.SerializerMethodField()

    class Meta:
        model = FamilyGroup
        fields = ["id", "name", "members"]

    def get_members(self, obj):
        return obj.member_set.count()


class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Profile
        fields = [
            "id",
            "photo",
            "mobile",
            "username",
            "latitude",
            "longitude",
        ]
        read_only_fields = ["id", "username"]


class MemberSerializer(serializers.ModelSerializer):
    group_name = serializers.CharField(source="group.name", read_only=True)
    qr = serializers.ImageField(read_only=True)
    photo = serializers.ImageField(read_only=True)

    class Meta:
        model = Member
        fields = [
            "id",
            "name",
            "father_name",
            "mobile",
            "relation",
            "age",
            "location",
            "organization",
            "place_visit",
            "emergency_contact",
            "photo",
            "qr",
            "group_name",
        ]
