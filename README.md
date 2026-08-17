# tools

Assorted utility scripts and tools

## Available tools

| Script                    | Description                                               |
| ------------------------- | --------------------------------------------------------- |
| `rclone/tree.sh`          | Sync between multiple rclone remotes via YAML config      |
| `rpm/compare.py`          | Compare installed rpm packages across systems via ssh     |
| `video/check_language.py` | Flag videos with a non-english default or extra languages |

## Development

    make          # create venv, install dependencies and the pre-commit hook
    make lint     # run pre-commit on all files
    make check    # run self-tests
