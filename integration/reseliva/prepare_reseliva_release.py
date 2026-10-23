"""Reproducibly add Reseliva to the exact current Ayseli static release."""
from pathlib import Path
import hashlib
import json
import shutil
import tarfile
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "ayseli-site"
TARGET = ROOT / "ayseli-reseliva"
BOOKING_URL = "https://www.reseliva.com/booknow/Ayseli-Otel/?lang=tr"
FAMILY_URL = "https://wa.me/905559610136?text=" + quote("Merhaba, çocuklu veya grup konaklaması için müsaitlik ve fiyat bilgisi almak istiyorum.")

def sha(data):
    return hashlib.sha256(data).hexdigest()

if not SOURCE.exists():
    archive = ROOT.parents[1] / "releases/2026-10-22/ayseli-release.tar.gz"
    assert sha(archive.read_bytes()) == "01088801c6087d481acee5073126bb34c066f5fdcab89325b80374465715e2a5"
    SOURCE.mkdir()
    with tarfile.open(archive) as tar:
        for member in tar.getmembers():
            assert member.isfile() and (SOURCE / member.name).resolve().is_relative_to(SOURCE.resolve())
        tar.extractall(SOURCE, filter="data")

if TARGET.exists():
    shutil.rmtree(TARGET)
shutil.copytree(SOURCE, TARGET)
html = (TARGET / "index.html").read_text()
page = next(TARGET.glob("_next/static/chunks/ayseli-page-*.js"))
js = page.read_text()

assert sha((SOURCE / "index.html").read_bytes()) == "be263e56138f7d9fa6a5b51f298090e0f25cc19e609caaa4835112a024fd096f", "Unexpected base release."

js = js.replace("window.ayseliMountConsent?.();", "window.ayseliMountConsent?.();window.ayseliMountReseliva?.();", 1)
start = js.index('(0,i.jsxs)("section",{className:"booking-wrap"')
end = js.index('(0,i.jsxs)("section",{className:"about section"', start)
intro = '(0,i.jsxs)("div",{className:"booking-intro",children:[(0,i.jsx)("span",{className:"eyebrow",children:"MERSİN’DE BİR MOLA"}),(0,i.jsxs)("p",{children:["Sizi ne zaman",(0,i.jsx)("br",{}),"ağırlayalım?"]})]})'
widget = '(0,i.jsx)("div",{id:"reseliva-widget",children:(0,i.jsx)("a",{href:"https://www.reseliva.com/",className:"powered_by",children:"Reseliva Rezervasyon Motoru & Kanal Yöneticisi"})})'
note = "Fiyat ve müsaitlik için Reseliva rezervasyon ekranına yönlendirilirsiniz."
js_section = '(0,i.jsxs)("section",{className:"booking-wrap",id:"rezervasyon","aria-label":"Online rezervasyon",children:[(0,i.jsxs)("div",{className:"booking booking-reseliva",children:[' + intro + ',' + widget + ']}),(0,i.jsxs)("div",{className:"booking-note reseliva-note",children:[(0,i.jsx)("p",{children:' + json.dumps(note, ensure_ascii=False) + '}),(0,i.jsx)("a",{id:"reseliva-direct-link",href:' + json.dumps(BOOKING_URL) + ',children:"Rezervasyon ekranını aç"}),(0,i.jsx)("p",{id:"reseliva-error",role:"alert","aria-live":"polite"})]})]}),'
js = js[:start] + js_section + js[end:]
family_js = '(0,i.jsx)("a",{href:' + json.dumps(FAMILY_URL) + ',onClick:el,children:"Çocuklu veya grup konaklaması için bize yazın"}),'
js = js.replace('(0,i.jsx)("a",{id:"reseliva-direct-link"', family_js + '(0,i.jsx)("a",{id:"reseliva-direct-link"', 1)

html_start = html.index('<section class="booking-wrap"')
html_end = html.index('<section class="about section"', html_start)
html_section = '<section class="booking-wrap" id="rezervasyon" aria-label="Online rezervasyon"><div class="booking booking-reseliva"><div class="booking-intro"><span class="eyebrow">MERSİN’DE BİR MOLA</span><p>Sizi ne zaman<br/>ağırlayalım?</p></div><div id="reseliva-widget"><a href="https://www.reseliva.com/" class="powered_by">Reseliva Rezervasyon Motoru &amp; Kanal Yöneticisi</a></div></div><div class="booking-note reseliva-note"><p>' + note + '</p><a id="reseliva-direct-link" href="' + BOOKING_URL + '">Rezervasyon ekranını aç</a><p id="reseliva-error" role="alert" aria-live="polite"></p></div></section>'
html = html[:html_start] + html_section + html[html_end:]
html = html.replace('<a id="reseliva-direct-link"', '<a href="' + FAMILY_URL + '">Çocuklu veya grup konaklaması için bize yazın</a><a id="reseliva-direct-link"', 1)

old_faq = "Tarihlerinizi ve misafir sayısını yukarıdaki formdan seçerek WhatsApp üzerinden müsaitlik talebi hazırlayabilir veya bizi arayabilirsiniz. Talep, kesin rezervasyon değildir; fiyat ve müsaitlik ekibimiz tarafından teyit edilir."
new_faq = "Tarihlerinizi ve misafir sayısını rezervasyon kutucuğundan seçip Fiyatları gör butonuna basabilirsiniz. Reseliva ekranında uygun odaları ve koşulları inceleyerek rezervasyonunuzu tamamlayabilirsiniz. Sorularınız ve grup talepleriniz için WhatsApp üzerinden bize ulaşabilir veya bizi arayabilirsiniz."
assert old_faq in js and old_faq in html
js = js.replace(old_faq, new_faq).replace('children:["Rezervasyon talebi ",', 'children:["Online rezervasyon ",')
html = html.replace(old_faq, new_faq).replace('>Rezervasyon talebi <', '>Online rezervasyon <')

old_privacy = "Bu sitedeki rezervasyon formu, seçtiğiniz tarih ve misafir sayısını WhatsApp’ta düzenleyebileceğiniz bir mesaja dönüştürür. Mesajı siz göndermeden otelimize talep iletilmez. Site üzerinde ödeme alınmaz veya kesin rezervasyon oluşturulmaz."
new_privacy = "Rezervasyon kutucuğu Reseliva tarafından sağlanır. Fiyatları gör butonuyla seçtiğiniz tarih ve kişi sayısı Reseliva rezervasyon ekranına aktarılır. Rezervasyon ve varsa ödeme işlemleri bu ekranda, gösterilen koşullara göre tamamlanır. WhatsApp bağlantıları ise siz göndermeden otelimize mesaj iletmez."
assert old_privacy in js
js = js.replace(old_privacy, new_privacy).replace("WhatsApp, Google Haritalar ve Instagram bağlantıları", "Reseliva, WhatsApp, Google Haritalar ve Instagram bağlantıları")

new_page_name = "ayseli-page-" + sha(js.encode())[:12] + ".js"
html = html.replace(page.name, new_page_name)
page.unlink()
page.with_name(new_page_name).write_text(js)

asset_names = {}
for source in ["reseliva-init.js", "reseliva-theme.css"]:
    content = (ROOT / source).read_bytes()
    p = Path(source)
    filename = p.stem + "-" + sha(content)[:12] + p.suffix
    (TARGET / filename).write_bytes(content)
    asset_names[p.stem] = filename

injection = '<link rel="stylesheet" href="/' + asset_names['reseliva-theme'] + '"/><script src="/' + asset_names['reseliva-init'] + '"></script>'
html = html.replace('<script src="/_next/', injection + '<script src="/_next/', 1)
(TARGET / "index.html").write_text(html)
manifest = json.loads((TARGET / "ayseli-release.json").read_text())
manifest.update({"release": "ayseli-reseliva-20261023", "base_release": "ayseli-phone-consent-20261022", "base_html_sha256": sha((SOURCE / "index.html").read_bytes()), "page_chunk": new_page_name, "booking_runtime": asset_names['reseliva-init'], "booking_stylesheet": asset_names['reseliva-theme'], "booking_url": BOOKING_URL, "files": len(list(p for p in TARGET.rglob('*') if p.is_file()))})
(TARGET / "ayseli-release.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"directory": str(TARGET), "page_chunk": new_page_name, **asset_names}, indent=2))
