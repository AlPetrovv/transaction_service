class SystemWalletDoesNotExist(Exception):
    msg = "System wallet does not exist"


class TransferError(Exception):
    msg = "Transfer failed"

    def __init__(self, message=None):
        self.message = message or self.msg