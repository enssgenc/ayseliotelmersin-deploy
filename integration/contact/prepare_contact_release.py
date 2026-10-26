"""Add the hotel's email to the verified Reseliva static release."""
from pathlib import Path
import hashlib
import io
import json
import tarfile

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "releases/2026-10-23/ayseli-reseliva-release.tar.gz"
OUTPUT = ROOT / "releases/2026-10-26/ayseli-contact-release.tar.gz"
EMAIL = "ayselihotel@gmail.com"

with tarfile.open(BASE) as archive:
    files = {entry.name: archive.extractfile(entry).read() for entry in archive if entry.isfile()}

html = files["index.html"].decode()
assert hashlib.sha256(files["index.html"]).hexdigest() == "2ac55c7c86f92afbf5bc34724e9477b1bf14ea5a8d53ced0616af56aee5ef130", "Unexpected base HTML"
manifest = json.loads(files["ayseli-release.json"])
old_chunk = "_next/static/chunks/" + manifest["page_chunk"]
js = files.pop(old_chunk).decode()

html_anchor = '<div class="contact-buttons">'
html_email = '<p style="font-size:15px">E-posta: <a href="mailto:' + EMAIL + '" style="text-decoration:underline;text-underline-offset:4px">' + EMAIL + '</a></p>'
js_anchor = '(0,i.jsxs)("div",{className:"contact-buttons"'
js_email = '(0,i.jsxs)("p",{style:{fontSize:"15px"},children:["E-posta: ",(0,i.jsx)("a",{href:"mailto:' + EMAIL + '",style:{textDecoration:"underline",textUnderlineOffset:"4px"},children:"' + EMAIL + '"})]}),'
assert html.count(html_anchor) == 1 and js.count(js_anchor) == 1
html = html.replace(html_anchor, html_email + html_anchor)
js = js.replace(js_anchor, js_email + js_anchor)

new_chunk = "ayseli-page-" + hashlib.sha256(js.encode()).hexdigest()[:12] + ".js"
html = html.replace(manifest["page_chunk"], new_chunk)
files["_next/static/chunks/" + new_chunk] = js.encode()
files["index.html"] = html.encode()
manifest.update(release="ayseli-contact-20261026", base_release="ayseli-reseliva-20261023", page_chunk=new_chunk, contact_email=EMAIL)
files["ayseli-release.json"] = (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode()

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
with tarfile.open(OUTPUT, "w:gz") as archive:
    for name, content in sorted(files.items()):
        entry = tarfile.TarInfo(name)
        entry.size = len(content)
        entry.mode = 0o644
        archive.addfile(entry, io.BytesIO(content))
print(json.dumps({"archive": str(OUTPUT), "sha256": hashlib.sha256(OUTPUT.read_bytes()).hexdigest(), "page_chunk": new_chunk, "files": len(files)}, indent=2))
