"""Service interfaces and adapters for bank account providers."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence
from datetime import datetime
from typing import Protocol

from move37.schemas.bank_account import AccountBalance, Transaction, TransferRequest


class OpenBankingClient(Protocol):
    """Minimal contract required by Open Banking-backed services."""

    def get_balance(self, account_id: str) -> AccountBalance:
        """Return the current balance for an account."""

    def list_transactions(
        self,
        account_id: str,
        start: datetime | None = None,
        end: datetime | None = None,
    ) -> Sequence[Transaction]:
        """Return transactions for an account."""

    def create_transfer(
        self,
        account_id: str,
        transfer: TransferRequest,
    ) -> str:
        """Create a transfer and return its identifier."""


class BankAccountInterface(ABC):
    """Contract for bank account service providers."""

    @abstractmethod
    def get_balance(self) -> AccountBalance:
        """Return the current account balance."""

    @abstractmethod
    def list_transactions(
        self,
        start: datetime | None = None,
        end: datetime | None = None,
    ) -> Sequence[Transaction]:
        """Return transactions within an optional time range."""

    @abstractmethod
    def transfer(self, transfer: TransferRequest) -> str:
        """Submit a transfer and return its identifier."""


class RevolutBankAccount(BankAccountInterface):
    """Revolut account adapter backed by an Open Banking client."""

    def __init__(self, account_id: str, open_banking_client: OpenBankingClient) -> None:
        self._account_id = account_id
        self._open_banking_client = open_banking_client

    def get_balance(self) -> AccountBalance:
        return self._open_banking_client.get_balance(self._account_id)

    def list_transactions(
        self,
        start: datetime | None = None,
        end: datetime | None = None,
    ) -> Sequence[Transaction]:
        return self._open_banking_client.list_transactions(
            account_id=self._account_id,
            start=start,
            end=end,
        )

    def transfer(self, transfer: TransferRequest) -> str:
        return self._open_banking_client.create_transfer(
            account_id=self._account_id,
            transfer=transfer,
        )
