"""Helpers for AWS/CDK deployment environment commands."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import os
from pathlib import Path
import shutil
import subprocess
from typing import Optional, Union


INFRA_RELATIVE_DIR = Path("src/move37/infra/eks")
STACK_VERSION_FILE = "stack-version.yaml"
REQUIRED_STACK_TARGETS = ("eks", "oidc", "access")


class InfraStackTarget(str, Enum):
    """Supported CDK stack targets."""

    eks = "eks"
    oidc = "oidc"
    access = "access"


@dataclass(frozen=True, slots=True)
class StackDefinition:
    """CDK entrypoint details for a single stack target."""

    stack_id: str
    app_command: Optional[str] = None


STACK_DEFINITIONS: dict[InfraStackTarget, StackDefinition] = {
    InfraStackTarget.eks: StackDefinition(stack_id="Move37EksStack"),
    InfraStackTarget.oidc: StackDefinition(
        stack_id="Move37GithubOidcBootstrapStack",
        app_command="npx ts-node --prefer-ts-exts bin/move37-github-oidc-bootstrap.ts",
    ),
    InfraStackTarget.access: StackDefinition(
        stack_id="Move37EksAccessRoleStack",
        app_command="npx ts-node --prefer-ts-exts bin/move37-eks-access-role.ts",
    ),
}


@dataclass(slots=True)
class InfraDoctorReport:
    """Result of inspecting local CDK prerequisites."""

    checks: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors


def infra_dir(repo_root: Union[str, Path]) -> Path:
    """Return the infra app directory under the repo root."""

    return Path(repo_root) / INFRA_RELATIVE_DIR


def collect_infra_doctor_report(repo_root: Union[str, Path]) -> InfraDoctorReport:
    """Inspect local infra/CDK prerequisites without mutating state."""

    root = Path(repo_root)
    workdir = infra_dir(root)
    report = InfraDoctorReport()

    if workdir.exists():
        report.checks.append(f"infra dir present: {workdir}")
    else:
        report.errors.append(f"infra dir missing: {workdir}")
        return report

    package_json = workdir / "package.json"
    if package_json.exists():
        report.checks.append(f"package manifest present: {package_json}")
    else:
        report.errors.append(f"package manifest missing: {package_json}")

    cdk_json = workdir / "cdk.json"
    if cdk_json.exists():
        report.checks.append(f"cdk manifest present: {cdk_json}")
    else:
        report.errors.append(f"cdk manifest missing: {cdk_json}")

    env_loader = workdir / "scripts" / "with-env.sh"
    if env_loader.exists():
        report.checks.append(f"env loader present: {env_loader}")
    else:
        report.errors.append(f"env loader missing: {env_loader}")

    stack_versions = _parse_stack_versions(workdir / STACK_VERSION_FILE)
    for stack_target in REQUIRED_STACK_TARGETS:
        if stack_target in stack_versions:
            report.checks.append(
                f"stack version present: {stack_target}={stack_versions[stack_target]}"
            )
        else:
            report.errors.append(f"stack version missing: {stack_target}")

    for command in ("bash", "git", "node", "npm", "npx"):
        path = shutil.which(command)
        if path:
            report.checks.append(f"{command} available: {path}")
        else:
            report.errors.append(f"{command} is not installed in the devtools runtime")

    node_modules = workdir / "node_modules"
    if node_modules.exists():
        report.checks.append(f"infra dependencies installed: {node_modules}")
    else:
        report.warnings.append(
            f"infra dependencies not installed yet: {node_modules} (run `infra deps`)"
        )

    region = os.environ.get("CDK_DEFAULT_REGION") or os.environ.get("AWS_REGION") or os.environ.get(
        "AWS_DEFAULT_REGION"
    )
    if region:
        report.checks.append(f"AWS region set: {region}")
    else:
        report.warnings.append("AWS region not set; CDK app will default to eu-central-1")

    account = os.environ.get("CDK_DEFAULT_ACCOUNT") or os.environ.get("AWS_ACCOUNT_ID")
    profile = os.environ.get("AWS_PROFILE")
    if account:
        report.checks.append(f"AWS account set explicitly: {account}")
    elif profile:
        report.checks.append(f"AWS profile set: {profile}")
    else:
        aws_dir = Path.home() / ".aws"
        if aws_dir.exists():
            report.checks.append(f"AWS config dir mounted: {aws_dir}")
        else:
            report.warnings.append(
                "no explicit AWS account/profile detected; CDK commands require usable AWS credentials"
            )

    return report


def install_infra_dependencies(repo_root: Union[str, Path]) -> None:
    """Install CDK app dependencies."""

    _run_command(["npm", "install"], cwd=infra_dir(repo_root))


def bootstrap_aws_environment(
    repo_root: Union[str, Path],
    extra_args: Optional[list[str]] = None,
) -> None:
    """Run `cdk bootstrap` in the infra app."""

    command = ["./scripts/with-env.sh", "cdk", "bootstrap"]
    if extra_args:
        command.extend(extra_args)
    _run_command(command, cwd=infra_dir(repo_root))


def synth_stack(
    repo_root: Union[str, Path],
    target: InfraStackTarget,
    extra_args: Optional[list[str]] = None,
) -> None:
    """Run `cdk synth` for a stack target."""

    _run_command(_build_cdk_stack_command("synth", target, extra_args=extra_args), cwd=infra_dir(repo_root))


def diff_stack(
    repo_root: Union[str, Path],
    target: InfraStackTarget,
    extra_args: Optional[list[str]] = None,
) -> None:
    """Run `cdk diff` for a stack target."""

    _run_command(_build_cdk_stack_command("diff", target, extra_args=extra_args), cwd=infra_dir(repo_root))


def deploy_stack(
    repo_root: Union[str, Path],
    target: InfraStackTarget,
    extra_args: Optional[list[str]] = None,
    require_approval: str = "never",
) -> None:
    """Run `cdk deploy` for a stack target."""

    _run_command(
        _build_cdk_stack_command(
            "deploy",
            target,
            extra_args=extra_args,
            require_approval=require_approval,
        ),
        cwd=infra_dir(repo_root),
    )


def _build_cdk_stack_command(
    action: str,
    target: InfraStackTarget,
    *,
    extra_args: Optional[list[str]] = None,
    require_approval: Optional[str] = None,
) -> list[str]:
    definition = STACK_DEFINITIONS[target]
    command = ["./scripts/with-env.sh", "cdk"]
    if definition.app_command:
        command.extend(["--app", definition.app_command])
    command.extend([action, definition.stack_id])
    if action == "deploy" and require_approval:
        command.extend(["--require-approval", require_approval])
    if extra_args:
        command.extend(extra_args)
    return command


def _parse_stack_versions(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    entries: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        entries[key.strip()] = value.strip()
    return entries


def _run_command(command: list[str], *, cwd: Path) -> None:
    subprocess.run(command, cwd=cwd, check=True)
