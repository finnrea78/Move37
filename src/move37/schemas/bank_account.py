"""Pydantic schemas for banking operations."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class Transaction(BaseModel):
    """Normalized bank transaction payload."""

    model_config = ConfigDict(extra="forbid")

    transaction_id: str
    booked_at: datetime
    amount: Decimal
    currency: str = Field(min_length=3, max_length=3)
    description: str | None = None
    counterparty: str | None = None
    metadata: dict[str, str] = Field(default_factory=dict)


class TransferRequest(BaseModel):
    """Input payload for account-to-account transfers."""

    model_config = ConfigDict(extra="forbid")

    amount: Decimal
    currency: str = Field(min_length=3, max_length=3)
    recipient_account_id: str
    reference: str


class AccountBalance(BaseModel):
    """Normalized bank balance response."""

    model_config = ConfigDict(extra="forbid")

    account_id: str
    amount: Decimal
    currency: str = Field(min_length=3, max_length=3)
