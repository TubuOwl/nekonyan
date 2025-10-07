import os
from bs4 import BeautifulSoup as bs
from requests import Session

os.makedirs("static/images", exist_ok=True)

def scrape_nekopoi_page(session: Session, page: int):
    if page == 1:
        url = "https://nekopoi.care/"
    else:
        url = f"https://nekopoi.care/page/{page}/"

    try:
        res = session.get(url, timeout=15)
        res.raise_for_status()
    except Exception as e:
        print(f"[ERROR] Page {page}: {e}")
        return []

    soup = bs(res.text, "html.parser")
    results = []

    for post in soup.select("div.eropost"):
        a_tag = post.select_one("div.eroinfo h2 a")
        img_tag = post.select_one("div.eroimg img")

        title = a_tag.text.strip() if a_tag else "N/A"
        link = a_tag["href"] if a_tag else "N/A"
        image_url = img_tag["src"] if img_tag else None

        local_path = None
        if image_url:
            try:
                img_res = session.get(image_url, headers={"Referer": "https://nekopoi.care"})
                filename = os.path.join("static/images", os.path.basename(image_url.split("?")[0]))
                with open(filename, "wb") as f:
                    f.write(img_res.content)
                local_path = "/static/images/" + os.path.basename(filename)
            except Exception as e:
                local_path = f"Failed: {e}"

        results.append({
            "title": title,
            "link": link,
            "image": local_path or "N/A"
        })

    return results


def scrape_nekopoi_all(pages=10):
    session = Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept-Language": "en-US,en;q=0.9"
    })
    all_results = []
    for i in range(1, pages + 1):
        print(f"Scraping page {i}...")
        all_results.extend(scrape_nekopoi_page(session, i))
    return all_results


def scrape_nekopoi_detail(link: str, session: Session = None) -> dict:
    if session is None:
        session = Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Referer": "https://nekopoi.care"
    })

    try:
        res = session.get(link, timeout=15)
        res.raise_for_status()
    except Exception as e:
        return {"error": f"Gagal ambil detail: {e}"}

    soup = bs(res.text, "html.parser")
    konten = soup.select_one("div.konten")
    if not konten:
        return {"error": "div.konten not found"}

    data = {
        "sinopsis": None, "genre": None, "producers": None,
        "duration": None, "size": None, "note": None, "streams": []
    }

    def get_text(tag):
        return tag.get_text(strip=True) if tag else None

    sinopsis_el = konten.find("b", string=lambda s: s and "Sinopsis" in s)
    if sinopsis_el:
        p_tag = sinopsis_el.find_parent("p")
        if p_tag and p_tag.find_next_sibling("p"):
            data["sinopsis"] = get_text(p_tag.find_next_sibling("p"))

    for label in ["Genre", "Producers", "Duration", "Size"]:
        el = konten.find(["b", "strong"], string=lambda s: s and label in s)
        if el:
            key = label.lower()
            data[key] = el.parent.get_text(strip=True).replace(label + " :", "").strip()

    note_el = konten.find("h3", string=lambda s: s and "Catatan" in s)
    if note_el:
        data["note"] = get_text(note_el)

    for i in range(1, 4):
        stream_div = soup.find("div", {"id": f"stream{i}", "class": "openstream"})
        if not stream_div:
            continue
        iframe = stream_div.find("iframe", src=True)
        if iframe and iframe["src"].startswith("https"):
            data["streams"].append(iframe["src"])

    return data
