from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from family.geo import parse_coords
from family.models import Profile
from wallet.models import Wallet
from .serializers import RegisterSerializer


@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        Wallet.objects.get_or_create(user=user)

        profile, _ = Profile.objects.get_or_create(user=user)
        lat, lng = parse_coords(request.data)
        if lat is not None and lng is not None:
            profile.latitude = lat
            profile.longitude = lng
            profile.save(update_fields=["latitude", "longitude"])

        return Response({"message": "registered"}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
