class TransferError(Exception):
    default_message = "Transfer failed"
    http_status = 500

    def __init__(self, message: str | None = None):
        super().__init__(message or self.default_message)
        self.message = message or self.default_message

    def __str__(self) -> str:
        return self.message


class WalletNotFound(TransferError):
    default_message = "Wallet not found"
    http_status = 404


class InsufficientFunds(TransferError):
    default_message = "Not enough balance"
    http_status = 422


class SelfTransferNotAllowed(TransferError):
    default_message = "Source and destination wallets must differ"
    http_status = 400


class SystemWalletDoesNotExist(TransferError):
    default_message = "System wallet is not configured"
    http_status = 503
