from decimal import Decimal

from rest_framework import serializers

from .models import Transaction
from .services import make_transfer


class TransferSerializer(serializers.Serializer):
    from_wallet_id = serializers.IntegerField(min_value=1)
    to_wallet_id = serializers.IntegerField(min_value=1)
    amount = serializers.DecimalField(
        max_digits=19,
        decimal_places=2,
        min_value=Decimal('0.01'),
    )

    def validate(self, attrs: dict) -> dict:
        if attrs['to_wallet_id'] == attrs['from_wallet_id']:
            raise serializers.ValidationError("Can't transfer to the same wallet")
        return attrs

    def create(self, validated_data: dict) -> Transaction:
        return make_transfer(
            from_wallet_id=validated_data['from_wallet_id'],
            to_wallet_id=validated_data['to_wallet_id'],
            amount=validated_data['amount'],
        )
