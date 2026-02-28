"""OpenAI-backed extractor implementation.

This adapter implements the ``Extractor`` port and is responsible for:

1. Selecting candidate files through a repository reader adapter.
2. Rendering the extraction prompt for each file.
3. Running a structured LLM call.
4. Converting results into orchestrator domain dataclasses.
"""

from __future__ import annotations

from hashlib import sha256

from opentelemetry import trace

from penroselamarck.orchestrator.config import OpenAISettings
from penroselamarck.orchestrator.github_crawler import GitHubRepositoryReader
from penroselamarck.orchestrator.models import ExtractedGuidelineCandidate, RepositoryTarget
from penroselamarck.orchestrator.ports import Extractor
from penroselamarck.orchestrator.prompts import load_prompt_set, render_user_prompt
from penroselamarck.orchestrator.providers.llm.openai.client import build_openai_chat_model
from penroselamarck.orchestrator.providers.llm.openai.schemas import ExtractionResult

_TRACER = trace.get_tracer("penroselamarck.orchestrator.openai")


class OpenAIExtractor(Extractor):
    """Extracts guideline candidates from repository text files via OpenAI."""

    def __init__(
        self,
        repository_reader: GitHubRepositoryReader,
        settings: OpenAISettings,
        max_files: int = 30,
        max_chars: int = 10000,
        prompt_version: str = "v1",
    ) -> None:
        self._reader = repository_reader
        self._max_files = max_files
        self._max_chars = max_chars
        self._prompt = load_prompt_set(step="extraction", version=prompt_version)
        llm = build_openai_chat_model(settings)
        self._structured_llm = llm.with_structured_output(ExtractionResult)

    def extract(self, target: RepositoryTarget) -> list[ExtractedGuidelineCandidate]:
        """Run extraction over candidate files for one repository target."""
        file_paths = self._reader.list_candidate_paths(target, max_files=self._max_files)
        candidates: list[ExtractedGuidelineCandidate] = []

        for file_path in file_paths:
            with _TRACER.start_as_current_span(
                "orchestrator.extract.llm_call",
                attributes={
                    "penroselamarck.repository": f"{target.owner}/{target.name}",
                    "penroselamarck.file_path": file_path,
                    "penroselamarck.prompt.step": self._prompt.step,
                    "penroselamarck.prompt.version": self._prompt.version,
                },
            ):
                file_text = self._reader.read_text(target, file_path, max_chars=self._max_chars)
                user_prompt = render_user_prompt(
                    self._prompt.user_template,
                    {
                        "repository": f"{target.owner}/{target.name}",
                        "file_path": file_path,
                        "file_text": file_text,
                    },
                )
                result = self._structured_llm.invoke([
                    ("system", self._prompt.system_prompt),
                    ("user", user_prompt),
                ])

            for item in result.items:
                title = item.title.strip()
                value = item.value.strip()
                if not title or not value:
                    continue
                digest = sha256(f"{file_path}\n{title}\n{value}".encode()).hexdigest()[:16]
                candidates.append(
                    ExtractedGuidelineCandidate(
                        file_path=file_path,
                        file_url=(
                            f"https://github.com/{target.owner}/{target.name}/blob/"
                            f"{target.head_sha}/{file_path}"
                        ),
                        title=title,
                        value=value,
                        rationale=(item.rationale or "").strip() or None,
                        class_names=[name.strip() for name in item.class_names if name.strip()],
                        source_hash=f"sha256:{digest}",
                        rationale_type=(item.rationale_type or "").strip() or None,
                    )
                )
        return candidates
