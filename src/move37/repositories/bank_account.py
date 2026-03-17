"""Repository for bank account connection records."""

from __future__ import annotations

from sqlalchemy.orm import Session

from move37.models.integrations import BankAccountConnectionModel


class BankAccountRepository:
    """SQLAlchemy repository for linked Open Banking accounts."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_provider_account(
        self,
        provider: str,
        external_account_id: str,
    ) -> BankAccountConnectionModel | None:
        return (
            self._session.query(BankAccountConnectionModel)
            .filter(BankAccountConnectionModel.provider == provider)
            .filter(BankAccountConnectionModel.external_account_id == external_account_id)
            .one_or_none()
        )

    def save(
        self,
        account: BankAccountConnectionModel,
    ) -> BankAccountConnectionModel:
        self._session.add(account)
        self._session.flush()
        return account
