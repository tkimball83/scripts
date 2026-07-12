#!/usr/bin/env python3

from __future__ import annotations

import sys
from pathlib import Path

import paramiko
from tabulate import tabulate

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from lib.output import spinner, status
from lib.runtime import run

REMOTE_COMMAND = (
    r"rpm -qa --queryformat "
    r"'%{NAME}.%{ARCH}\t%|EPOCH?{%{EPOCH}:}:{}|%{VERSION}-%{RELEASE}\n'"
)
SSH_TIMEOUT = 30
IGNORED_PACKAGES = {"gpg-pubkey"}


def connect_settings(host: str) -> dict:
    config = paramiko.SSHConfig()
    path = Path.home() / ".ssh" / "config"
    if path.exists():
        with path.open() as handle:
            config.parse(handle)
    entry = config.lookup(host)
    settings = {
        "hostname": entry.get("hostname", host),
        "port": int(entry.get("port", 22)),
        "timeout": SSH_TIMEOUT,
    }
    if "user" in entry:
        settings["username"] = entry["user"]
    if "identityfile" in entry:
        settings["key_filename"] = entry["identityfile"]
    return settings


def gather_packages(host: str) -> dict[str, set[str]]:
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(**connect_settings(host))
        _, stdout, stderr = client.exec_command(REMOTE_COMMAND, timeout=SSH_TIMEOUT)
        output = stdout.read().decode()
        if stdout.channel.recv_exit_status() != 0:
            detail = stderr.read().decode().strip().splitlines()
            raise RuntimeError(detail[-1] if detail else "remote rpm query failed")
    finally:
        client.close()
    packages: dict[str, set[str]] = {}
    for line in output.splitlines():
        name, _, version = line.partition("\t")
        if not name or not version:
            continue
        if name.rsplit(".", 1)[0] in IGNORED_PACKAGES:
            continue
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
        except (OSError, RuntimeError, paramiko.SSHException) as exc:
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
