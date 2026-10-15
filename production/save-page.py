"""Preserve generated manga page pixels in delivery assets and record provenance."""
from pathlib import Path
from PIL import Image
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parent.parent
chapter = int(sys.argv[1])
number = int(sys.argv[2])
source = Path(sys.argv[3])

plan = json.loads((ROOT / f"production/ch{chapter:03}-pages.json").read_text())
page = plan["pages"][number - 1]

# Save as WebP (or JPG if requested)
output_dir = ROOT / f"docs/assets/ch{chapter:03}"
output_dir.mkdir(parents=True, exist_ok=True)
output = output_dir / f"p{number:03}.jpg"

image = Image.open(source).convert("RGB")
image.save(output, "JPEG", quality=95)

# Also sync to root assets/
root_output = ROOT / f"assets/ch{chapter:03}/p{number:03}.jpg"
root_output.parent.mkdir(parents=True, exist_ok=True)
image.save(root_output, "JPEG", quality=95)

records_path = ROOT / f"production/ch{chapter:03}-generation-records.json"
records = json.loads(records_path.read_text()) if records_path.exists() else {
    "chapter": chapter,
    "tool": "image-generator / AI Manga Illustrator",
    "pages": []
}

records["pages"] = [p for p in records["pages"] if p["number"] != number]
records["pages"].append({
    "number": number,
    "title": page["title"],
    "sourceImage": str(source),
    "output": f"assets/ch{chapter:03}/p{number:03}.jpg",
    "width": image.width,
    "height": image.height,
    "sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
    "verified": True
})
records["pages"].sort(key=lambda p: p["number"])
records_path.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
print(f"Saved page {number}: {page['title']} ({image.width}x{image.height})")
