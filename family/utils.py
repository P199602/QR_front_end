import qrcode
from django.conf import settings
from django.core.files import File
from io import BytesIO


def member_scan_url(member):
    """Public URL encoded in the QR (opens the React scan page)."""
    base = getattr(settings, "FRONTEND_URL", "http://localhost:5173").rstrip("/")
    return f"{base}/scan/{member.qr_token}"


def create_qr(member):
    url = member_scan_url(member)
    image = qrcode.make(url)
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)
    member.qr.save(f"member_{member.id}.png", File(buffer), save=True)
