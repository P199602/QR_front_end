from django.urls import path
from . import views

urlpatterns = [
    path("wallet/", views.wallet_detail),
    path("wallet/add/", views.wallet_add),
]
