from django.urls import path

from app.views import TransferAPIView

app_name = 'app'

urlpatterns = [
    path("transfer/", TransferAPIView.as_view(), name="transfer"),
]