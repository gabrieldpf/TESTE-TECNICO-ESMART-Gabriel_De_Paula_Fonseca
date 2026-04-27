import csv
from pathlib import Path
from typing import Any, Dict, List

EXPORT_FIELDS = [
    "id",
    "alt",
    "width",
    "height",
    "photographer",
    "photographer_url",
]


def export_photos_to_csv(photos: List[Dict[str, Any]], output_path: str) -> Path:
    path = Path(output_path).expanduser().resolve()
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=EXPORT_FIELDS)
        writer.writeheader()
        for photo in photos:
            writer.writerow({field: photo.get(field, "") for field in EXPORT_FIELDS})

    return path
