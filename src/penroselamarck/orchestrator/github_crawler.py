"""GitHub org/repository scope resolution and repository file access."""

from __future__ import annotations

import base64
import json
from dataclasses import dataclass
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.request import Request, urlopen

from penroselamarck.orchestrator.config import GitHubAPISettings, OrchestratorScope
from penroselamarck.orchestrator.models import RepositoryTarget
from penroselamarck.utils.error import OrchestratorScopeConfigError

_CANDIDATE_EXTENSIONS = (".md", ".rst", ".txt", ".adoc")
_CANDIDATE_MARKERS = (
    "guideline",
    "guidelines",
    "architecture",
    "pattern",
    "standards",
    "contributing",
    "readme",
)


@dataclass(frozen=True)
class GitHubRepositoryRef:
    owner: str
    name: str

    @property
    def key(self) -> str:
        return f"{self.owner}/{self.name}".lower()


class GitHubAPIClient:
    """Minimal GitHub REST API client for orchestrator workflows."""

    def __init__(self, settings: GitHubAPISettings) -> None:
        self._settings = settings

    def list_org_repositories(self, org: str) -> list[GitHubRepositoryRef]:
        repositories: list[GitHubRepositoryRef] = []
        page = 1
        while True:
            payload = self._github_json(f"/orgs/{org}/repos?type=all&per_page=100&page={page}")
            if not payload:
                break
            for item in payload:
                owner = (item.get("owner", {}) or {}).get("login") or org
                name = (item.get("name") or "").strip()
                if not name:
                    continue
                repositories.append(GitHubRepositoryRef(owner=owner, name=name))
            page += 1
        return repositories

    def get_repository(self, owner: str, name: str) -> dict:
        return self._github_json(f"/repos/{owner}/{name}")

    def get_head_sha(self, owner: str, name: str, branch: str) -> str:
        payload = self._github_json(f"/repos/{owner}/{name}/commits/{quote(branch, safe='')}")
        sha = (payload.get("sha") or "").strip()
        if not sha:
            raise RuntimeError(f"Head commit SHA not found for repository {owner}/{name}.")
        return sha

    def list_repository_tree_paths(self, owner: str, name: str, head_sha: str) -> list[str]:
        payload = self._github_json(f"/repos/{owner}/{name}/git/trees/{head_sha}?recursive=1")
        tree = payload.get("tree", [])
        paths = [
            item["path"]
            for item in tree
            if item.get("type") == "blob" and isinstance(item.get("path"), str)
        ]
        return sorted(paths)

    def read_repository_text_file(self, owner: str, name: str, path: str, ref: str) -> str:
        payload = self._github_json(
            f"/repos/{owner}/{name}/contents/{quote(path, safe='/')}" f"?ref={quote(ref, safe='')}"
        )
        encoded = payload.get("content")
        encoding = (payload.get("encoding") or "").lower()
        if not encoded or encoding != "base64":
            raise RuntimeError(f"Unable to read file content for {owner}/{name}:{path}.")
        return base64.b64decode(encoded.encode("utf-8")).decode("utf-8", errors="replace")

    def _github_json(self, path: str):
        url = f"{self._settings.api_url}{path}"
        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "penroselamarck-orchestrator",
        }
        if self._settings.token:
            headers["Authorization"] = f"Bearer {self._settings.token}"

        request = Request(url=url, headers=headers, method="GET")
        try:
            with urlopen(request, timeout=self._settings.request_timeout_seconds) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            if exc.code == 404:
                raise RuntimeError(f"GitHub resource not found: {url}") from exc
            raise RuntimeError(f"GitHub API request failed ({exc.code}): {url}") from exc
        except Exception as exc:  # pragma: no cover - defensive error mapping
            raise RuntimeError(f"GitHub API request failed: {url}") from exc


class GitHubOrgRepoCrawler:
    """Resolves orchestrator repository targets from org/repo scope."""

    def __init__(self, client: GitHubAPIClient) -> None:
        self._client = client

    def resolve_targets(self, scope: OrchestratorScope) -> list[RepositoryTarget]:
        if not scope.enabled:
            return []

        explicit_refs = self._parse_explicit_repo_refs(scope.repositories)
        if explicit_refs:
            refs = [ref for ref in explicit_refs if ref.owner in set(scope.organisations)]
        else:
            refs = []
            for org in scope.organisations:
                refs.extend(self._client.list_org_repositories(org))

        deduped: dict[str, GitHubRepositoryRef] = {}
        for ref in refs:
            deduped[ref.key] = ref

        targets: list[RepositoryTarget] = []
        for ref in sorted(deduped.values(), key=lambda item: item.key):
            repo = self._client.get_repository(ref.owner, ref.name)
            default_branch = (repo.get("default_branch") or "").strip()
            if not default_branch:
                continue
            head_sha = self._client.get_head_sha(ref.owner, ref.name, default_branch)
            targets.append(
                RepositoryTarget(
                    owner=ref.owner,
                    name=ref.name,
                    repo_url=f"https://github.com/{ref.owner}/{ref.name}",
                    default_branch=default_branch,
                    head_sha=head_sha,
                )
            )
        return targets

    def _parse_explicit_repo_refs(self, repositories: list[str]) -> list[GitHubRepositoryRef]:
        refs: list[GitHubRepositoryRef] = []
        for repo in repositories:
            candidate = repo.strip().strip("/")
            if not candidate:
                continue
            if "/" not in candidate:
                raise OrchestratorScopeConfigError(
                    message=(
                        "Invalid GITHUB_REPOSITORIES entry " f"'{candidate}' (expected owner/repo)"
                    ),
                    hint="Use entries like genentech/penrose-lamarck.",
                )
            owner, name = candidate.split("/", 1)
            if not owner or not name:
                raise OrchestratorScopeConfigError(
                    message=(
                        "Invalid GITHUB_REPOSITORIES entry " f"'{candidate}' (expected owner/repo)"
                    ),
                    hint="Use entries like genentech/penrose-lamarck.",
                )
            refs.append(GitHubRepositoryRef(owner=owner, name=name))
        return refs


class GitHubRepositoryReader:
    """Reads guideline candidate files from GitHub repositories."""

    def __init__(self, client: GitHubAPIClient) -> None:
        self._client = client

    def list_candidate_paths(self, target: RepositoryTarget, max_files: int = 30) -> list[str]:
        paths = self._client.list_repository_tree_paths(
            owner=target.owner,
            name=target.name,
            head_sha=target.head_sha,
        )
        selected: list[str] = []
        for path in paths:
            lower = path.lower()
            if not lower.endswith(_CANDIDATE_EXTENSIONS):
                continue
            if not any(marker in lower for marker in _CANDIDATE_MARKERS):
                continue
            selected.append(path)
            if len(selected) >= max_files:
                break
        return selected

    def read_text(self, target: RepositoryTarget, path: str, max_chars: int = 10000) -> str:
        content = self._client.read_repository_text_file(
            owner=target.owner,
            name=target.name,
            path=path,
            ref=target.head_sha,
        )
        return content[:max_chars]
