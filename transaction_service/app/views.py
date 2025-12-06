import logging

from rest_framework.response import Response
from rest_framework.views import APIView

from .exceptions import TransferError
from .models import Transaction
from .serializers import TransferSerializer
from .tasks import send_notification

logger = logging.getLogger(__name__)

class TransferAPIView(APIView):
    serializer_class = TransferSerializer
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            transaction: Transaction = serializer.save()
        except TransferError as exc:
            logger.error("Transfer failed", exc_info=True)
            return Response({"error": str(exc)}, status=500)
        except Exception:  # noqa
            logger.error("Transfer failed", exc_info=True)
            return Response({"error": "Transfer failed"}, status=500)
        send_notification.apply_async()

        return Response({
            'transaction_id': transaction.id,
            'created_at': transaction.created_at,
        }, status=201)
