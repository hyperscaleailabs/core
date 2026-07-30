#!/usr/bin/env python3
"""Workflow hygiene guards: keep CI checks runnable locally and honest.

Three rules, each one a defect this repository actually shipped:

1. **Piped steps set pipefail.** GitHub's default shell is ``bash -e {0}``,
   which does *not* set ``pipefail``. A step written ``npm run build | tee
   build.txt`` therefore reports the exit status of ``tee``, and a failing
   build passes the gate. Found live in ``atlas.yml``. A step that pipes into
   ``tee`` must either declare ``shell: bash`` (which brings ``-eo pipefail``)
   or set ``pipefail`` in the body.

2. **Module policy guards live in a script.** A guard that exists only as
   workflow YAML is first exercised on a hosted runner, after the handoff -
   lesson L6, ``atlas/docs/lessons/2026-07-28-atlas-integration.md``. Every
   ``*-policy-guards`` job must be a call to a ``check-policy.sh``, never an
   inline grep.

3. **Every module Makefile has a ``verify`` target.** ``verify`` is the
   contract that one command runs the module's gates; without it a contributor
   has to read the workflow to find out what will fail.

Requires: pyyaml. Exit 1 on any violation.
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

import yaml

WORKFLOWS = Path(".github/workflows")
POLICY_JOB_SUFFIX = "-policy-guards"
POLICY_SCRIPT_CALL = re.compile(r"^bash\s+\S*check-policy\.sh\s*$")


def steps_of(job: dict) -> list[dict]:
    return [s for s in (job.get("steps") or []) if isinstance(s, dict)]


def check_pipefail(workflows: dict[Path, dict]) -> list[str]:
    problems = []
    for path, doc in workflows.items():
        for job_id, job in (doc.get("jobs") or {}).items():
            if not isinstance(job, dict):
                continue
            job_shell = ((job.get("defaults") or {}).get("run") or {}).get("shell")
            for step in steps_of(job):
                run = step.get("run")
                if not isinstance(run, str) or "| tee" not in run:
                    continue
                shell = step.get("shell") or job_shell
                if shell == "bash" or "pipefail" in run:
                    continue
                name = step.get("name") or run.strip().splitlines()[0]
                problems.append(
                    f"{path}: job '{job_id}', step '{name}' pipes into tee "
                    f"without pipefail; add `shell: bash` or `set -o pipefail`"
                )
    return problems


def check_policy_jobs_are_scripts(workflows: dict[Path, dict]) -> list[str]:
    problems = []
    for path, doc in workflows.items():
        for job_id, job in (doc.get("jobs") or {}).items():
            if not isinstance(job, dict) or not job_id.endswith(POLICY_JOB_SUFFIX):
                continue
            runs = [s["run"] for s in steps_of(job) if isinstance(s.get("run"), str)]
            if not runs:
                problems.append(f"{path}: job '{job_id}' has no run step")
                continue
            for run in runs:
                if not POLICY_SCRIPT_CALL.match(run.strip()):
                    first = run.strip().splitlines()[0]
                    problems.append(
                        f"{path}: job '{job_id}' runs an inline guard "
                        f"({first!r}); move it into a check-policy.sh so it can "
                        f"be run before pushing"
                    )
    return problems


def check_makefiles_have_verify() -> list[str]:
    problems = []
    for makefile in sorted(Path(".").glob("*/Makefile")):
        text = makefile.read_text()
        if not re.search(r"^verify:", text, re.MULTILINE):
            problems.append(
                f"{makefile}: no `verify` target; one command must run the "
                f"module's gates"
            )
    return problems


def main() -> int:
    os.chdir(Path(__file__).resolve().parents[2])

    if not WORKFLOWS.is_dir():
        print(f"::error::{WORKFLOWS} not found")
        return 1

    workflows: dict[Path, dict] = {}
    for path in sorted(WORKFLOWS.glob("*.yml")) + sorted(WORKFLOWS.glob("*.yaml")):
        doc = yaml.safe_load(path.read_text())
        if isinstance(doc, dict):
            workflows[path] = doc

    checks = [
        ("piped steps set pipefail", check_pipefail(workflows)),
        ("policy guards live in a script", check_policy_jobs_are_scripts(workflows)),
        ("every module Makefile has a verify target", check_makefiles_have_verify()),
    ]

    status = 0
    for title, problems in checks:
        print(f"== {title} ==")
        if problems:
            for p in problems:
                print(f"::error::{p}")
            status = 1
        else:
            print("ok")

    if status == 0:
        print("")
        print("CI hygiene OK")
    return status


if __name__ == "__main__":
    sys.exit(main())
