from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

# Set RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET in environment to enable payments.
try:
    import razorpay
    import os

    _key = os.environ.get("RAZORPAY_KEY_ID", "")
    _secret = os.environ.get("RAZORPAY_KEY_SECRET", "")
    client = razorpay.Client(auth=(_key, _secret)) if _key and _secret else None
except ImportError:
    client = None


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_order(request):
    if not client:
        return Response(
            {"error": "Payment gateway not configured."},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    try:
        amount = int(request.data.get("amount", 0)) * 100
    except (TypeError, ValueError):
        return Response({"error": "Invalid amount."}, status=status.HTTP_400_BAD_REQUEST)

    if amount <= 0:
        return Response({"error": "Amount must be positive."}, status=status.HTTP_400_BAD_REQUEST)

    order = client.order.create({"amount": amount, "currency": "INR", "payment_capture": 1})
    return Response(order)
