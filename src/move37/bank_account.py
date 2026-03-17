"""Compatibility exports for banking integration types."""

from .schemas.bank_account import AccountBalance, Transaction, TransferRequest
from .services.bank_account import (
    BankAccountInterface,
    OpenBankingClient,
    RevolutBankAccount,
)

__all__ = [
    "AccountBalance",
    "BankAccountInterface",
    "OpenBankingClient",
    "RevolutBankAccount",
    "Transaction",
    "TransferRequest",
]
