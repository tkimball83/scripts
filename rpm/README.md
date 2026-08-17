# rpm

Compare installed RPM packages across remote systems via SSH.

## Requirements

| Requirement                                            | Description               |
| ------------------------------------------------------ | ------------------------- |
| [tabulate](https://github.com/astanin/python-tabulate) | Pretty-print tabular data |
| [yaspin](https://github.com/pavdmyt/yaspin)            | Terminal spinner          |

Hosts must be reachable with passwordless (key-based) SSH; the script connects
with `BatchMode=yes` and will not prompt for a password.

## Usage

    python compare.py HOST HOST [HOST ...]

## Examples

    python compare.py server1 server2
    python compare.py web01 web02 web03
