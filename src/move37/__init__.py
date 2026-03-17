"""Move37 integration package organized for FastAPI applications."""

from .repositories import (
    ActivityGraphRepository,
    BankAccountRepository,
    CalendarConnectionRepository,
    GitHubIntegrationRepository,
)
from .schemas import (
    AccountBalance,
    CalendarEvent,
    CalendarEventUpdate,
    GitHubIssue,
    GitHubIssueCreate,
    GitHubPullRequest,
    GitHubRepository,
    GitHubWorkflowDispatch,
    Transaction,
    TransferRequest,
)
from .services import (
    ActivityGraphService,
    AppleCalendar,
    BankAccountInterface,
    CalendarInterface,
    GitHubInterface,
    GoogleCalendar,
    OpenBankingClient,
    RevolutBankAccount,
    ServiceContainer,
)

__all__ = [
    "AccountBalance",
    "ActivityGraphRepository",
    "ActivityGraphService",
    "AppleCalendar",
    "BankAccountInterface",
    "BankAccountRepository",
    "CalendarConnectionRepository",
    "CalendarEvent",
    "CalendarEventUpdate",
    "CalendarInterface",
    "GitHubIntegrationRepository",
    "GitHubInterface",
    "GitHubIssue",
    "GitHubIssueCreate",
    "GitHubPullRequest",
    "GitHubRepository",
    "GitHubWorkflowDispatch",
    "GoogleCalendar",
    "OpenBankingClient",
    "RevolutBankAccount",
    "ServiceContainer",
    "Transaction",
    "TransferRequest",
]
