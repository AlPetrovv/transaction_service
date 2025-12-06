from decimal import Decimal

from rest_framework import serializers

from .models import Transaction
from .services import make_transfer


class TransferSerializer(serializers.Serializer):
    to_wallet_id = serializers.IntegerField(min_value=1)
    from_wallet_id = serializers.IntegerField(min_value=1)
    amount = serializers.DecimalField(max_digits=18, decimal_places=2, min_value=Decimal('0.01'))

    def validate(self, attrs: dict):
        from_wallet_id: int = attrs["from_wallet_id"]
        to_wallet_id: int = attrs["to_wallet_id"]

        if to_wallet_id == from_wallet_id:
            raise serializers.ValidationError("Can't transfer to the same wallet")
        return attrs

    def create(self, validated_data: dict) -> Transaction:
        amount: Decimal = validated_data['amount']
        from_wallet: int = validated_data['from_wallet_id']
        to_wallet: int = validated_data['to_wallet_id']
        tx = make_transfer(
            from_wallet_id=from_wallet,
            to_wallet_id=to_wallet,
            amount=amount
        )
        return tx
