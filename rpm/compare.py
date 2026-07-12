#!/usr/bin/env python3

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from tabulate import tabulate

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from lib.output import spinner, status
from lib.runtime import run

IGNORED_PACKAGES = {"gpg-pubkey"}
REMOTE_COMMAND = (
    r"rpm -qa --queryformat "
    r"'%{NAME}.%{ARCH}\t%|EPOCH?{%{EPOCH}:}:{}|%{VERSION}-%{RELEASE}\n'"
)


def gather_packages(host: str) -> dict[str, set[str]]:
    result = subprocess.run(
        ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=10", host, REMOTE_COMMAND],
        capture_output=True,
        text=True,
        timeout=30,
    )
    if result.returncode != 0:
        detail = result.stderr.strip().splitlines()
        raise RuntimeError(detail[-1] if detail else f"ssh exited {result.returncode}")
    output = result.stdout
    packages: dict[str, set[str]] = {}
    malformed = 0
    for line in output.splitlines():
        name, _, version = line.partition("\t")
        if not name or not version:
            malformed += bool(line.strip())
            continue
        if name.rsplit(".", 1)[0] in IGNORED_PACKAGES:
            continue
        packages.setdefault(name, set()).add(version)
    if malformed:
        raise RuntimeError(f"{malformed} unrecognized line(s) in rpm output")
    return packages


def main() -> int:
    if not 3 <= len(sys.argv) <= 4:
        status(f"USAGE: {Path(sys.argv[0]).name} HOST HOST [HOST]")
        return 2
    hosts = sys.argv[1:]
    if len(set(hosts)) != len(hosts):
        status(f"USAGE: {Path(sys.argv[0]).name} HOST HOST [HOST]")
        return 2

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
