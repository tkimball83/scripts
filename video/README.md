# video

Flag video files with a non-English default audio track or extra non-English languages.

Only files with a recognized video extension (per Python's `mimetypes`) are scanned.

## Requirements

| Requirement                                            | Description               |
| ------------------------------------------------------ | ------------------------- |
| [libmediainfo](https://mediaarea.net/MediaInfo)        | Media metadata library    |
| [pymediainfo](https://github.com/sbraz/pymediainfo)    | MediaInfo wrapper         |
| [tabulate](https://github.com/astanin/python-tabulate) | Pretty-print tabular data |
| [yaspin](https://github.com/pavdmyt/yaspin)            | Terminal spinner          |

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
