"""
core.py - Ortak yükleme mantığı / Shared upload logic
Hem GUI hem CLI tarafından kullanılır. / Used by both the GUI and the CLI.
"""

import os
import re
import csv
import json
import time
import pickle
from datetime import datetime

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
VIDEO_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv", ".webm", ".m4v"}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")
TOKEN_PATH = os.path.join(BASE_DIR, "token.pickle")
PROGRESS_PATH = os.path.join(BASE_DIR, "progress.json")
RESULTS_CSV = os.path.join(BASE_DIR, "yuklenen_videolar.csv")

DEFAULT_CONFIG = {
    "video_klasoru": "",
    "client_secrets_dosyasi": "client_secret.json",
    "ozel_aciklama_metni": "",
    "gizlilik": "unlisted",
    "tarih_deseni": r"\d{4}[-_.]\d{2}[-_.]\d{2}",
    "baslik_sablonu": "{tarih} - {dosya_adi}",
    "aciklama_sablonu": "{baslik}\nTarih: {tarih}\n\n{ozel_metin}",
    "etiketler": [],
    "gunluk_yukleme_limiti": 6,
}


# ---------------------------------------------------------------------------
# Ayarlar / Config
# ---------------------------------------------------------------------------

def load_config():
    if not os.path.exists(CONFIG_PATH):
        save_config(DEFAULT_CONFIG)
        return dict(DEFAULT_CONFIG)
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    merged = dict(DEFAULT_CONFIG)
    merged.update(cfg)
    return merged


def save_config(cfg):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# İlerleme kaydı (kaldığı yerden devam) / Progress tracking (resume)
# ---------------------------------------------------------------------------

def load_progress():
    if os.path.exists(PROGRESS_PATH):
        with open(PROGRESS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_progress(progress):
    with open(PROGRESS_PATH, "w", encoding="utf-8") as f:
        json.dump(progress, f, ensure_ascii=False, indent=2)


def write_results_csv(progress):
    with open(RESULTS_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["dosya", "baslik", "tarih", "video_id", "link", "durum"])
        writer.writeheader()
        for info in progress.values():
            writer.writerow(info)


# ---------------------------------------------------------------------------
# Google kimlik doğrulama / Google authentication
# ---------------------------------------------------------------------------

def get_authenticated_service(client_secrets_file):
    creds = None
    if os.path.exists(TOKEN_PATH):
        with open(TOKEN_PATH, "rb") as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(client_secrets_file, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_PATH, "wb") as token:
            pickle.dump(creds, token)
    return build("youtube", "v3", credentials=creds)


def is_authenticated():
    return os.path.exists(TOKEN_PATH)


def clear_authentication():
    if os.path.exists(TOKEN_PATH):
        os.remove(TOKEN_PATH)


# ---------------------------------------------------------------------------
# Dosya adından tarih / başlık / açıklama üretimi
# ---------------------------------------------------------------------------

def extract_date_from_filename(filename, date_regex):
    try:
        match = re.search(date_regex, filename)
    except re.error:
        match = None
    if match:
        return match.group(0)
    return None


def fallback_date_from_file(filepath):
    ts = os.path.getmtime(filepath)
    return datetime.fromtimestamp(ts).strftime("%Y-%m-%d")


def build_title(filename_no_ext, date_str, title_template):
    clean_name = re.sub(r"[_\-]+", " ", filename_no_ext).strip()
    try:
        return title_template.format(dosya_adi=clean_name, tarih=date_str)[:100]
    except (KeyError, IndexError):
        return f"{date_str} - {clean_name}"[:100]


def build_description(title, date_str, custom_text, description_template):
    try:
        return description_template.format(baslik=title, tarih=date_str, ozel_metin=custom_text)[:5000]
    except (KeyError, IndexError):
        return f"{title}\n{date_str}\n\n{custom_text}"[:5000]


def list_video_files(folder):
    if not os.path.isdir(folder):
        return []
    return sorted(
        f for f in os.listdir(folder)
        if os.path.splitext(f)[1].lower() in VIDEO_EXTENSIONS
    )


# ---------------------------------------------------------------------------
# Yükleme / Upload
# ---------------------------------------------------------------------------

def upload_video(youtube, filepath, title, description, privacy_status, tags, progress_callback=None):
    """
    progress_callback(fraction: float) her chunk sonrası çağrılır (0.0 - 1.0).
    """
    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
        },
        "status": {
            "privacyStatus": privacy_status,
            "selfDeclaredMadeForKids": False,
        },
    }

    media = MediaFileUpload(filepath, chunksize=1024 * 1024 * 4, resumable=True, mimetype="video/*")
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)

    response = None
    retries = 0
    while response is None:
        try:
            status, response = request.next_chunk()
            if status and progress_callback:
                progress_callback(status.progress())
        except HttpError as e:
            if e.resp.status in (500, 502, 503, 504) and retries < 5:
                retries += 1
                time.sleep(5)
                continue
            raise
    return response["id"]


def run_upload_batch(cfg, log=print, on_item_done=None, should_stop=None):
    """
    cfg: config dict
    log(str): satır satır ilerleme mesajı basar
    on_item_done(info_dict): her video tamamlandığında çağrılır (Treeview güncellemek için)
    should_stop(): True dönerse döngü durur (kullanıcı 'Durdur' dediyse)
    """
    video_folder = cfg["video_klasoru"]
    client_secrets_file = cfg["client_secrets_dosyasi"]
    custom_text = cfg["ozel_aciklama_metni"]
    privacy_status = cfg.get("gizlilik", "unlisted")
    date_regex = cfg.get("tarih_deseni") or DEFAULT_CONFIG["tarih_deseni"]
    title_template = cfg.get("baslik_sablonu") or DEFAULT_CONFIG["baslik_sablonu"]
    description_template = cfg.get("aciklama_sablonu") or DEFAULT_CONFIG["aciklama_sablonu"]
    tags = cfg.get("etiketler", [])
    daily_limit = int(cfg.get("gunluk_yukleme_limiti", 6))

    if not os.path.isdir(video_folder):
        log(f"HATA: video klasörü bulunamadı: {video_folder}")
        return

    if not os.path.exists(client_secrets_file):
        log(f"HATA: client_secrets dosyası bulunamadı: {client_secrets_file}")
        return

    files = list_video_files(video_folder)
    if not files:
        log("HATA: klasörde desteklenen uzantıda video bulunamadı.")
        return

    progress = load_progress()
    log("Google hesabına bağlanılıyor (tarayıcı açılabilir)...")
    youtube = get_authenticated_service(client_secrets_file)
    log("Bağlantı başarılı.")

    uploaded_this_run = 0

    for fname in files:
        if should_stop and should_stop():
            log("Kullanıcı tarafından durduruldu.")
            break

        if fname in progress and progress[fname].get("durum") == "tamamlandı":
            log(f"[ATLANDI - zaten yüklü] {fname}")
            continue

        if uploaded_this_run >= daily_limit:
            log(f"Bu çalıştırma için limite ulaşıldı ({daily_limit}). "
                f"Kalanlar için programı tekrar açıp devam edin.")
            break

        filepath = os.path.join(video_folder, fname)
        name_no_ext = os.path.splitext(fname)[0]
        date_str = extract_date_from_filename(fname, date_regex) or fallback_date_from_file(filepath)
        title = build_title(name_no_ext, date_str, title_template)
        description = build_description(title, date_str, custom_text, description_template)

        log(f"Yükleniyor: {fname}  (başlık: {title})")

        def _cb(frac, fname=fname):
            log(f"    {fname}: %{int(frac * 100)}")

        try:
            video_id = upload_video(youtube, filepath, title, description, privacy_status, tags, _cb)
        except HttpError as e:
            log(f"    HATA: {fname} yüklenemedi -> {e}")
            info = {"dosya": fname, "baslik": title, "tarih": date_str,
                     "video_id": "", "link": "", "durum": "hata"}
            progress[fname] = info
            save_progress(progress)
            write_results_csv(progress)
            if on_item_done:
                on_item_done(info)
            continue

        url = f"https://youtu.be/{video_id}"
        log(f"    Tamamlandı: {url}")
        info = {"dosya": fname, "baslik": title, "tarih": date_str,
                 "video_id": video_id, "link": url, "durum": "tamamlandı"}
        progress[fname] = info
        save_progress(progress)
        write_results_csv(progress)
        if on_item_done:
            on_item_done(info)
        uploaded_this_run += 1

    log(f"\nBu çalıştırmada {uploaded_this_run} video yüklendi. "
        f"Toplam CSV: {RESULTS_CSV}")
