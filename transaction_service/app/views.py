import logging

from rest_framework.response import Response
from rest_framework.views import APIView

from .exceptions import TransferError
from .serializers import TransferSerializer

logger = logging.getLogger(__name__)


class TransferAPIView(APIView):
    serializer_class = TransferSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            tx = serializer.save()
        except TransferError as exc:
            logger.warning("Transfer rejected: %s", exc)
            return Response({"error": str(exc)}, status=exc.http_status)

        return Response(
            {"transaction_id": tx.pk, "created_at": tx.created_at},
            status=201,
        )
