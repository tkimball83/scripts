# video

Flag video files with a non-English default audio track or extra non-English languages.

## Requirements

| Requirement                                            | Description               |
| ------------------------------------------------------ | ------------------------- |
| [pymediainfo](https://github.com/sbraz/pymediainfo)    | MediaInfo wrapper         |
| [tabulate](https://github.com/astanin/python-tabulate) | Pretty-print tabular data |

## Usage

    python check_language.py DIR [DIR ...]

## Environment

| Variable  | Default | Description                       |
| --------- | ------- | --------------------------------- |
| `WORKERS` | `8`     | Number of concurrent scan threads |

## Examples

    python check_language.py /media/movies
    python check_language.py /media/movies /media/tv
    WORKERS=4 python check_language.py /media/movies
