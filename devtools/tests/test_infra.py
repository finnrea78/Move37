from __future__ import annotations

from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from mv37_devtools.infra import (
    InfraStackTarget,
    _build_cdk_stack_command,
    collect_infra_doctor_report,
    install_infra_dependencies,
)


class InfraTest(unittest.TestCase):
    def test_build_cdk_command_for_eks_uses_default_app(self) -> None:
        command = _build_cdk_stack_command("synth", InfraStackTarget.eks)

        self.assertEqual(
            command,
            ["./scripts/with-env.sh", "cdk", "synth", "Move37EksStack"],
        )

    def test_build_cdk_command_for_oidc_sets_stack_app(self) -> None:
        command = _build_cdk_stack_command(
            "deploy",
            InfraStackTarget.oidc,
            require_approval="never",
            extra_args=["--verbose"],
        )

        self.assertIn("--app", command)
        self.assertIn("Move37GithubOidcBootstrapStack", command)
        self.assertEqual(command[-3:], ["--require-approval", "never", "--verbose"])

    def test_collect_infra_doctor_report_reads_stack_versions(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            infra_dir = repo_root / "src" / "move37" / "infra" / "eks"
            scripts_dir = infra_dir / "scripts"
            node_modules = infra_dir / "node_modules"
            scripts_dir.mkdir(parents=True)
            node_modules.mkdir()
            (infra_dir / "package.json").write_text("{}", encoding="utf-8")
            (infra_dir / "cdk.json").write_text("{}", encoding="utf-8")
            (scripts_dir / "with-env.sh").write_text("#!/usr/bin/env bash\n", encoding="utf-8")
            (infra_dir / "stack-version.yaml").write_text(
                "eks: 1\noidc: 1\naccess: 1\n",
                encoding="utf-8",
            )

            with patch("mv37_devtools.infra.shutil.which", return_value="/usr/bin/fake"):
                report = collect_infra_doctor_report(repo_root)

        self.assertTrue(report.ok)
        self.assertFalse(report.errors)

    def test_install_infra_dependencies_runs_npm_install(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            infra_dir = repo_root / "src" / "move37" / "infra" / "eks"
            infra_dir.mkdir(parents=True)

            with patch("mv37_devtools.infra.subprocess.run") as run:
                install_infra_dependencies(repo_root)

        run.assert_called_once_with(["npm", "install"], cwd=infra_dir, check=True)
