# rclone

A YAML-controlled bash script to sync between multiple rclone remotes.

## Requirements

| Requirement                                | Description               |
| ------------------------------------------ | ------------------------- |
| [rclone](https://github.com/rclone/rclone) | rsync for cloud storage   |
| [shyaml](https://github.com/0k/shyaml)     | YAML for the command line |

## Usage

    bash tree.sh [options]

## Options

| Flag | Default                   | Description                         |
| ---- | ------------------------- | ----------------------------------- |
| `-2` | `false`                   | Enable HTTP/2 for rclone            |
| `-b` | `rclone`                  | Change path to rclone binary        |
| `-c` | `null`                    | Change path to rclone config        |
| `-d` | `false`                   | Enable dry run and command output   |
| `-f` | `tree.yaml`               | Change path to script config YAML   |
| `-k` | `32`                      | Change rclone checkers setting      |
| `-l` | `0`                       | Change rclone bandwidth limit       |
| `-s` | `shyaml`                  | Change path to shyaml binary        |
| `-t` | `16`                      | Change rclone transfers setting     |

If `-c` is not provided, the script uses the first existing config at:
`~/.config/rclone/rclone.conf`, then `/etc/rclone/rclone.conf`.

## Examples

    bash tree.sh -d
    bash tree.sh -2
    bash tree.sh -k 16
    bash tree.sh -l 100M
    bash tree.sh -b ~/.local/bin/rclone -c ~/.config/rclone/rclone.conf
    bash tree.sh -s /opt/homebrew/bin/shyaml
