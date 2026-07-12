#!/usr/bin/env python3

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from tabulate import tabulate

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from lib.output import spinner, status
from lib.runtime import run

REMOTE_COMMAND = """python3 -c 'import rpm
for h in rpm.TransactionSet().dbMatch():
    epoch = h[rpm.RPMTAG_EPOCH]
    prefix = "%s:" % epoch if epoch is not None else ""
    print(
        "%s.%s\\t%s%s-%s"
        % (
            h[rpm.RPMTAG_NAME],
            h[rpm.RPMTAG_ARCH] or "(none)",
            prefix,
            h[rpm.RPMTAG_VERSION],
            h[rpm.RPMTAG_RELEASE],
        )
    )'"""
SSH_TIMEOUT = 120


def gather_packages(host: str) -> dict[str, set[str]]:
    result = subprocess.run(
        ["ssh", "-o", "BatchMode=yes", host, REMOTE_COMMAND],
        capture_output=True,
        text=True,
        timeout=SSH_TIMEOUT,
    )
    if result.returncode != 0:
        detail = result.stderr.strip().splitlines()
        raise RuntimeError(detail[-1] if detail else f"ssh exited {result.returncode}")
    packages: dict[str, set[str]] = {}
    for line in result.stdout.splitlines():
        name, _, version = line.partition("\t")
        if name and version:
            packages.setdefault(name, set()).add(version)
    return packages


def main() -> int:
    if len(sys.argv) < 3:
        status(f"USAGE: {Path(sys.argv[0]).name} HOST HOST [HOST ...]")
        return 2
    hosts = sys.argv[1:]

    inventories = {}
    errors = 0
    for host in hosts:
        try:
            with spinner(f"Gathering packages from {host}"):
                inventories[host] = gather_packages(host)
        except (OSError, RuntimeError, subprocess.TimeoutExpired) as exc:
            errors += 1
            status(f"ERROR: {host}: {exc}")
            continue
        status(f"Found {len(inventories[host])} package(s) on {host}")
    if errors:
        return 1

    names = sorted(set().union(*inventories.values()))
    rows = []
    for name in names:
        versions = [
            ",".join(sorted(inventories[host].get(name, ()))) or "-" for host in hosts
        ]
        if len(set(versions)) > 1:
            rows.append((name, *versions))

    if rows:
        table = tabulate(rows, headers=["Package", *hosts], tablefmt="simple")
        print(f"\n{table}\n")

    status(
        f"Compared {len(names)} package(s) across {len(hosts)} host(s), {len(rows)} difference(s)."
    )
    return 0


if __name__ == "__main__":
    run(main)
