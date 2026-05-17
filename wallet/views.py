from decimal import Decimal, InvalidOperation

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Wallet, WalletTransaction


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def wallet_detail(request):
    wallet, _ = Wallet.objects.get_or_create(user=request.user)
    return Response({"balance": float(wallet.balance)})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def wallet_add(request):
    try:
        amount = Decimal(str(request.data.get("amount", "5")))
    except (InvalidOperation, TypeError):
        return Response({"error": "Invalid amount."}, status=status.HTTP_400_BAD_REQUEST)

    if amount <= 0:
        return Response({"error": "Amount must be positive."}, status=status.HTTP_400_BAD_REQUEST)

    wallet, _ = Wallet.objects.get_or_create(user=request.user)
    wallet.balance += amount
    wallet.save(update_fields=["balance"])

    WalletTransaction.objects.create(
        user=request.user,
        amount=amount,
        transaction_type="credit",
    )

    return Response({"balance": float(wallet.balance), "message": "Money added"})
