"""
Authentication service.

Provides token-based login and demo user retrieval.

Public API
----------
- :class:`Auth0Settings`: Auth0 configuration container.
- :class:`Auth0Identity`: Auth0 identity data.
- :class:`Auth0TokenVerifier`: Auth0 JWT verifier.
- :class:`AuthService`: Authentication operations.

Attributes
----------
None

Examples
--------
>>> from penroselamarck.repositories.user_repository import UserRepository
>>> service = AuthService(UserRepository())
>>> isinstance(service.login("token").user_id, str)
True

See Also
--------
:mod:`penroselamarck.repositories.user_repository`
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from threading import Lock
from typing import Any
from urllib.request import Request, urlopen

import jwt
from jwt import InvalidTokenError
from jwt.algorithms import RSAAlgorithm

from penroselamarck.repositories.user_repository import UserRecord, UserRepository
from penroselamarck.services.errors import ValidationError


@dataclass(frozen=True)
class Auth0Settings:
    """
    Auth0Settings(
        domain,
        audience,
        issuer,
        jwks_url,
        algorithms,
        roles_claim,
        clock_skew_seconds,
        jwks_cache_ttl_seconds,
        jwks_timeout_seconds) -> Auth0Settings

    Concise (one-line) description of the settings container.

    Parameters
    ----------
    domain : str
        Auth0 tenant domain (without scheme).
    audience : str
        API audience identifier.
    issuer : str
        Expected issuer for tokens.
    jwks_url : str
        URL to fetch Auth0 JWKS keys.
    algorithms : List[str]
        Allowed JWT algorithms.
    roles_claim : str
        Claim name that stores roles/permissions.
    clock_skew_seconds : int
        Allowed clock skew in seconds.
    jwks_cache_ttl_seconds : int
        Time-to-live for cached JWKS keys.
    jwks_timeout_seconds : int
        Network timeout for JWKS fetches.

    Returns
    -------
    Auth0Settings
        Immutable Auth0 settings.
    """

    domain: str
    audience: str
    issuer: str
    jwks_url: str
    algorithms: list[str]
    roles_claim: str
    clock_skew_seconds: int
    jwks_cache_ttl_seconds: int
    jwks_timeout_seconds: int

    @classmethod
    def from_env(cls) -> Auth0Settings | None:
        """
        from_env() -> Optional[Auth0Settings]

        Concise (one-line) description of the function.

        Parameters
        ----------
        None
            This function does not accept parameters.

        Returns
        -------
        Optional[Auth0Settings]
            Settings loaded from environment or None if Auth0 is not configured.

        Throws
        ------
        ValueError
            Raised when only one of `AUTH0_DOMAIN` or `AUTH0_AUDIENCE` is set.

        Examples
        --------
        >>> isinstance(Auth0Settings.from_env(), (Auth0Settings, type(None)))
        True
        """
        raw_domain = os.environ.get("AUTH0_DOMAIN")
        audience = os.environ.get("AUTH0_AUDIENCE")
        if raw_domain and not audience:
            raise ValueError("AUTH0_AUDIENCE must be set when AUTH0_DOMAIN is set.")
        if audience and not raw_domain:
            raise ValueError("AUTH0_DOMAIN must be set when AUTH0_AUDIENCE is set.")
        if not raw_domain or not audience:
            return None
        domain = raw_domain.replace("https://", "").replace("http://", "").rstrip("/")
        issuer = os.environ.get("AUTH0_ISSUER") or f"https://{domain}/"
        if not issuer.endswith("/"):
            issuer = issuer + "/"
        jwks_url = os.environ.get("AUTH0_JWKS_URL") or f"https://{domain}/.well-known/jwks.json"
        algorithms = [
            value.strip()
            for value in os.environ.get("AUTH0_ALGORITHMS", "RS256").split(",")
            if value.strip()
        ]
        roles_claim = os.environ.get("AUTH0_ROLES_CLAIM", "permissions")
        clock_skew_seconds = int(os.environ.get("AUTH0_CLOCK_SKEW_SECONDS", "60"))
        jwks_cache_ttl_seconds = int(os.environ.get("AUTH0_JWKS_CACHE_TTL_SECONDS", "600"))
        jwks_timeout_seconds = int(os.environ.get("AUTH0_JWKS_TIMEOUT_SECONDS", "5"))
        return cls(
            domain=domain,
            audience=audience,
            issuer=issuer,
            jwks_url=jwks_url,
            algorithms=algorithms,
            roles_claim=roles_claim,
            clock_skew_seconds=clock_skew_seconds,
            jwks_cache_ttl_seconds=jwks_cache_ttl_seconds,
            jwks_timeout_seconds=jwks_timeout_seconds,
        )


@dataclass(frozen=True)
class Auth0Identity:
    """
    Auth0Identity(user_id, roles, claims) -> Auth0Identity

    Concise (one-line) description of the identity container.

    Parameters
    ----------
    user_id : str
        Authenticated user identifier.
    roles : List[str]
        Roles or permissions derived from the token.
    claims : Dict
        Decoded JWT claims.

    Returns
    -------
    Auth0Identity
        Immutable identity data.
    """

    user_id: str
    roles: list[str]
    claims: dict[str, Any]


class Auth0JwksCache:
    """
    Auth0JwksCache(jwks_url, cache_ttl_seconds, timeout_seconds) -> Auth0JwksCache

    Concise (one-line) description of the JWKS cache.

    Methods
    -------
    get_key(kid)
        Return a public key for the specified key id.
    """

    def __init__(self, jwks_url: str, cache_ttl_seconds: int, timeout_seconds: int) -> None:
        """
        __init__(jwks_url, cache_ttl_seconds, timeout_seconds) -> None

        Concise (one-line) description of the initializer.

        Parameters
        ----------
        jwks_url : str
            URL to fetch JWKS keys.
        cache_ttl_seconds : int
            Cache lifetime in seconds.
        timeout_seconds : int
            Network timeout in seconds.

        Returns
        -------
        None
            Initializes the JWKS cache.

        Examples
        --------
        >>> isinstance(Auth0JwksCache("https://example.com", 60, 5), Auth0JwksCache)
        True
        """
        self._jwks_url = jwks_url
        self._cache_ttl_seconds = cache_ttl_seconds
        self._timeout_seconds = timeout_seconds
        self._lock = Lock()
        self._expires_at = 0.0
        self._keys_by_kid: dict[str, Any] = {}

    def get_key(self, kid: str) -> Any:
        """
        get_key(kid) -> Any

        Concise (one-line) description of the function.

        Parameters
        ----------
        kid : str
            Key identifier from JWT header.

        Throws
        ------
        ValidationError
            Raised when the key cannot be resolved or fetched.

        Returns
        -------
        Any
            Public key object for JWT verification.

        Examples
        --------
        >>> cache = Auth0JwksCache("https://example.com", 60, 5)
        >>> isinstance(cache._keys_by_kid, dict)
        True
        """
        if not kid:
            raise ValidationError("Token header missing key id.")
        now = time.time()
        with self._lock:
            if not self._keys_by_kid or now >= self._expires_at:
                self._keys_by_kid = self._fetch_keys()
                self._expires_at = now + self._cache_ttl_seconds
            key = self._keys_by_kid.get(kid)
        if key is None:
            raise ValidationError("Token signing key not found.")
        return key

    def _fetch_keys(self) -> dict[str, Any]:
        """
        _fetch_keys() -> Dict[str, Any]

        Concise (one-line) description of the function.

        Parameters
        ----------
        None
            This function does not accept parameters.

        Throws
        ------
        ValidationError
            Raised when the JWKS payload is unavailable or invalid.

        Returns
        -------
        Dict[str, Any]
            Mapping of key id to parsed public keys.

        Examples
        --------
        >>> isinstance(Auth0JwksCache("https://example.com", 60, 5)._keys_by_kid, dict)
        True
        """
        request = Request(self._jwks_url, headers={"Accept": "application/json"})
        try:
            with urlopen(request, timeout=self._timeout_seconds) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except Exception as exc:
            raise ValidationError("Unable to fetch Auth0 JWKS.") from exc
        keys = payload.get("keys")
        if not isinstance(keys, list) or not keys:
            raise ValidationError("Auth0 JWKS payload missing keys.")
        parsed: dict[str, Any] = {}
        for key in keys:
            kid = key.get("kid") if isinstance(key, dict) else None
            if not kid:
                continue
            parsed[kid] = RSAAlgorithm.from_jwk(json.dumps(key))
        if not parsed:
            raise ValidationError("Auth0 JWKS did not contain usable keys.")
        return parsed


class Auth0TokenVerifier:
    """
    Auth0TokenVerifier(settings, jwks_cache=None) -> Auth0TokenVerifier

    Concise (one-line) description of the Auth0 token verifier.

    Methods
    -------
    verify(token)
        Validate a JWT and return Auth0 identity data.
    """

    def __init__(
        self,
        settings: Auth0Settings,
        jwks_cache: Auth0JwksCache | None = None,
    ) -> None:
        """
        __init__(settings, jwks_cache=None) -> None

        Concise (one-line) description of the initializer.

        Parameters
        ----------
        settings : Auth0Settings
            Auth0 configuration settings.
        jwks_cache : Optional[Auth0JwksCache]
            Optional JWKS cache override.

        Returns
        -------
        None
            Initializes the verifier.

        Examples
        --------
        >>> settings = Auth0Settings(
        ...     domain="example.com",
        ...     audience="aud",
        ...     issuer="https://example.com/",
        ...     jwks_url="https://example.com/.well-known/jwks.json",
        ...     algorithms=["RS256"],
        ...     roles_claim="permissions",
        ...     clock_skew_seconds=60,
        ...     jwks_cache_ttl_seconds=600,
        ...     jwks_timeout_seconds=5,
        ... )
        >>> isinstance(Auth0TokenVerifier(settings), Auth0TokenVerifier)
        True
        """
        self._settings = settings
        self._jwks_cache = jwks_cache or Auth0JwksCache(
            settings.jwks_url,
            settings.jwks_cache_ttl_seconds,
            settings.jwks_timeout_seconds,
        )

    def verify(self, token: str) -> Auth0Identity:
        """
        verify(token) -> Auth0Identity

        Concise (one-line) description of the function.

        Parameters
        ----------
        token : str
            JWT access token to validate.

        Throws
        ------
        ValidationError
            Raised when the token is invalid or missing required claims.

        Returns
        -------
        Auth0Identity
            Authenticated identity information.

        Examples
        --------
        >>> isinstance(Auth0TokenVerifier.__name__, str)
        True
        """
        claims = self._decode_claims(token)
        user_id = claims.get("sub")
        if not user_id:
            raise ValidationError("Token missing subject.")
        roles = self._extract_roles(claims)
        return Auth0Identity(user_id=user_id, roles=roles, claims=claims)

    def _decode_claims(self, token: str) -> dict[str, Any]:
        """
        _decode_claims(token) -> Dict[str, Any]

        Concise (one-line) description of the function.

        Parameters
        ----------
        token : str
            JWT access token to decode.

        Throws
        ------
        ValidationError
            Raised when decoding fails.

        Returns
        -------
        Dict[str, Any]
            Decoded JWT claims.

        Examples
        --------
        >>> isinstance(Auth0TokenVerifier.__name__, str)
        True
        """
        if not token:
            raise ValidationError("Token is required.")
        try:
            header = jwt.get_unverified_header(token)
        except Exception as exc:
            raise ValidationError("Invalid token header.") from exc
        kid = header.get("kid")
        if not kid:
            raise ValidationError("Token header missing key id.")
        key = self._jwks_cache.get_key(kid)
        try:
            return jwt.decode(
                token,
                key=key,
                algorithms=self._settings.algorithms,
                audience=self._settings.audience,
                issuer=self._settings.issuer,
                leeway=self._settings.clock_skew_seconds,
                options={"require": ["exp", "sub"]},
            )
        except InvalidTokenError as exc:
            raise ValidationError("Token validation failed.") from exc

    def _extract_roles(self, claims: dict[str, Any]) -> list[str]:
        """
        _extract_roles(claims) -> List[str]

        Concise (one-line) description of the function.

        Parameters
        ----------
        claims : Dict[str, Any]
            Decoded JWT claims.

        Returns
        -------
        List[str]
            Normalized role or permission list.

        Examples
        --------
        >>> isinstance(Auth0TokenVerifier.__name__, str)
        True
        """
        raw = claims.get(self._settings.roles_claim)
        if raw is None and self._settings.roles_claim != "permissions":
            raw = claims.get("permissions")
        if raw is None:
            raw = claims.get("scope")
        if raw is None:
            return []
        if isinstance(raw, str):
            return [value for value in raw.split() if value]
        if isinstance(raw, list):
            return [str(value) for value in raw if value]
        return [str(raw)]


class AuthService:
    """
    AuthService(user_repository, auth0_settings=None) -> AuthService

    Concise (one-line) description of the service.

    Methods
    -------
    login(token)
        Authenticate or create a user for a token.
    demo_user()
        Return the demo user record.
    """

    def __init__(
        self,
        user_repository: UserRepository,
        auth0_settings: Auth0Settings | None = None,
    ) -> None:
        """
        __init__(user_repository, auth0_settings=None) -> None

        Concise (one-line) description of the initializer.

        Parameters
        ----------
        user_repository : UserRepository
            Repository for user storage.
        auth0_settings : Optional[Auth0Settings]
            Optional Auth0 settings override.

        Returns
        -------
        None
            Initializes the service.

        Throws
        ------
        ValueError
            Raised when Auth0 environment configuration is incomplete.

        Examples
        --------
        >>> isinstance(AuthService(UserRepository()), AuthService)
        True
        """
        self._user_repository = user_repository
        self._auth0_settings = auth0_settings or Auth0Settings.from_env()
        self._auth0_verifier = (
            Auth0TokenVerifier(self._auth0_settings) if self._auth0_settings else None
        )

    def login(self, token: str) -> UserRecord:
        """
        login(token) -> UserRecord

        Concise (one-line) description of the function.

        Parameters
        ----------
        token : str
            Authentication token.

        Throws
        ------
        ValidationError
            Raised when Auth0 token validation fails.

        Returns
        -------
        UserRecord
            Authenticated user record.

        Examples
        --------
        >>> isinstance(AuthService(UserRepository()).login(\"demo\"), UserRecord)
        True
        """
        if self._auth0_verifier is None:
            return self._user_repository.get_or_create(token)
        identity = self._auth0_verifier.verify(token)
        return self._user_repository.get_or_create(
            identity.user_id,
            user_id=identity.user_id,
            roles=identity.roles,
        )

    def demo_user(self) -> UserRecord:
        """
        demo_user() -> UserRecord

        Concise (one-line) description of the function.

        Parameters
        ----------
        None
            This function does not accept parameters.

        Returns
        -------
        UserRecord
            Demo user record.
        """
        return self._user_repository.get_demo_user()
