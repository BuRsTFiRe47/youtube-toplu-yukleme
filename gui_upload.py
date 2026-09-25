#!/usr/bin/env python3
"""
gui_upload.py - YouTube Toplu Video Yükleme Aracı (Arayüzlü Sürüm)
====================================================================
Tech-savvy olmayan kullanıcılar için basit, karanlık temalı arayüz.
Ayarlar sekmesi, canlı yükleme günlüğü ve daha önce yüklenen videoları
gösteren bir geçmiş tablosu içerir. Program kapatılıp tekrar açıldığında
zaten yüklenmiş videoları otomatik atlar (kaldığı yerden devam eder).

Çalıştırmak için: python gui_upload.py
"""

import os
import sys
import threading
import queue
import webbrowser
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

import core

# ---------------------------------------------------------------------------
# Karanlık tema renkleri / Dark theme colors
# ---------------------------------------------------------------------------
BG = "#1e1e1e"
BG_PANEL = "#252526"
FG = "#e0e0e0"
FG_DIM = "#9a9a9a"
ENTRY_BG = "#2d2d30"
ACCENT = "#4caf50"
ACCENT_HOVER = "#5cc561"
DANGER = "#e05252"
BORDER = "#3a3a3a"


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("YouTube Toplu Video Yükleme Aracı")
        self.geometry("880x620")
        self.configure(bg=BG)
        self.minsize(760, 560)

        self.cfg = core.load_config()
        self.log_queue = queue.Queue()
        self.upload_thread = None
        self.stop_flag = False

        self._build_style()
        self._build_layout()
        self._load_history()
        self.after(150, self._drain_log_queue)

    # ------------------------------------------------------------------
    # Stil / Style
    # ------------------------------------------------------------------
    def _build_style(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure(".", background=BG, foreground=FG, fieldbackground=ENTRY_BG,
                         bordercolor=BORDER, lightcolor=BG, darkcolor=BG)
        style.configure("TFrame", background=BG)
        style.configure("Panel.TFrame", background=BG_PANEL)
        style.configure("TLabel", background=BG, foreground=FG)
        style.configure("Dim.TLabel", background=BG, foreground=FG_DIM)
        style.configure("TNotebook", background=BG, bordercolor=BG)
        style.configure("TNotebook.Tab", background=BG_PANEL, foreground=FG, padding=(16, 8))
        style.map("TNotebook.Tab", background=[("selected", ACCENT)],
                  foreground=[("selected", "#0d0d0d")])
        style.configure("TEntry", fieldbackground=ENTRY_BG, foreground=FG, insertcolor=FG)
        style.configure("TCombobox", fieldbackground=ENTRY_BG, foreground=FG,
                         background=ENTRY_BG, arrowcolor=FG)
        style.map("TCombobox", fieldbackground=[("readonly", ENTRY_BG)])
        style.configure("TButton", background=BG_PANEL, foreground=FG, padding=8, borderwidth=0)
        style.map("TButton", background=[("active", BORDER)])
        style.configure("Accent.TButton", background=ACCENT, foreground="#0d0d0d", padding=10)
        style.map("Accent.TButton", background=[("active", ACCENT_HOVER)])
        style.configure("Danger.TButton", background=DANGER, foreground="#0d0d0d", padding=10)
        style.configure("Treeview", background=ENTRY_BG, fieldbackground=ENTRY_BG,
                         foreground=FG, rowheight=26, borderwidth=0)
        style.configure("Treeview.Heading", background=BG_PANEL, foreground=FG, borderwidth=0)
        style.map("Treeview", background=[("selected", ACCENT)], foreground=[("selected", "#0d0d0d")])
        style.configure("Horizontal.TProgressbar", background=ACCENT, troughcolor=BG_PANEL)

    # ------------------------------------------------------------------
    # Genel yerleşim / Layout
    # ------------------------------------------------------------------
    def _build_layout(self):
        header = ttk.Frame(self, style="Panel.TFrame")
        header.pack(fill="x")
        ttk.Label(header, text="YouTube Toplu Video Yükleme Aracı",
                  font=("Segoe UI", 15, "bold"), style="Panel.TFrame" if False else "TLabel",
                  background=BG_PANEL).pack(side="left", padx=16, pady=14)

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.tab_settings = ttk.Frame(self.notebook)
        self.tab_upload = ttk.Frame(self.notebook)
        self.tab_history = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_settings, text="  Ayarlar  ")
        self.notebook.add(self.tab_upload, text="  Yükleme  ")
        self.notebook.add(self.tab_history, text="  Geçmiş  ")

        self._build_settings_tab()
        self._build_upload_tab()
        self._build_history_tab()

    # ------------------------------------------------------------------
    # Ayarlar sekmesi / Settings tab
    # ------------------------------------------------------------------
    def _build_settings_tab(self):
        f = self.tab_settings
        for i in range(3):
            f.columnconfigure(1, weight=1)

        row = 0

        def add_row(label_text, widget, hint=None):
            nonlocal row
            ttk.Label(f, text=label_text).grid(row=row, column=0, sticky="nw", padx=(4, 10), pady=(10, 0))
            widget.grid(row=row, column=1, sticky="ew", pady=(10, 0))
            row += 1
            if hint:
                ttk.Label(f, text=hint, style="Dim.TLabel", wraplength=520,
                          font=("Segoe UI", 8)).grid(row=row, column=1, sticky="w")
                row += 1

        # Video klasörü
        folder_frame = ttk.Frame(f)
        self.var_folder = tk.StringVar(value=self.cfg.get("video_klasoru", ""))
        ttk.Entry(folder_frame, textvariable=self.var_folder).pack(side="left", fill="x", expand=True)
        ttk.Button(folder_frame, text="Klasör Seç...", command=self._pick_folder).pack(side="left", padx=(6, 0))
        add_row("Video Klasörü:", folder_frame, "Yüklenecek videoların bulunduğu klasör.")

        # client_secret.json
        secrets_frame = ttk.Frame(f)
        self.var_secrets = tk.StringVar(value=self.cfg.get("client_secrets_dosyasi", "client_secret.json"))
        ttk.Entry(secrets_frame, textvariable=self.var_secrets).pack(side="left", fill="x", expand=True)
        ttk.Button(secrets_frame, text="Dosya Seç...", command=self._pick_secrets).pack(side="left", padx=(6, 0))
        add_row("client_secret.json:", secrets_frame, "Google Cloud Console'dan indirdiğiniz OAuth dosyası (README'e bakın).")

        # Özel açıklama metni
        self.txt_custom = tk.Text(f, height=5, bg=ENTRY_BG, fg=FG, insertbackground=FG,
                                   relief="flat", wrap="word")
        self.txt_custom.insert("1.0", self.cfg.get("ozel_aciklama_metni", ""))
        add_row("Açıklamaya Eklenecek Sabit Metin:", self.txt_custom,
                "Her videonun açıklamasına otomatik eklenecek metin (ör. basın kartı başvuru metni).")

        # Gizlilik
        self.var_privacy = tk.StringVar(value=self.cfg.get("gizlilik", "unlisted"))
        privacy_combo = ttk.Combobox(f, textvariable=self.var_privacy, state="readonly",
                                      values=["private", "unlisted", "public"])
        add_row("Gizlilik:", privacy_combo,
                "private: sadece siz, unlisted: linki olan herkes, public: herkese açık.")

        # Başlık şablonu
        self.var_title_tpl = tk.StringVar(value=self.cfg.get("baslik_sablonu", core.DEFAULT_CONFIG["baslik_sablonu"]))
        add_row("Başlık Şablonu:", ttk.Entry(f, textvariable=self.var_title_tpl),
                "Kullanılabilir: {tarih}, {dosya_adi}")

        # Açıklama şablonu
        self.txt_desc_tpl = tk.Text(f, height=4, bg=ENTRY_BG, fg=FG, insertbackground=FG,
                                     relief="flat", wrap="word")
        self.txt_desc_tpl.insert("1.0", self.cfg.get("aciklama_sablonu", core.DEFAULT_CONFIG["aciklama_sablonu"]))
        add_row("Açıklama Şablonu:", self.txt_desc_tpl,
                "Kullanılabilir: {baslik}, {tarih}, {ozel_metin}")

        # Tarih deseni
        self.var_date_regex = tk.StringVar(value=self.cfg.get("tarih_deseni", core.DEFAULT_CONFIG["tarih_deseni"]))
        add_row("Dosya Adından Tarih Deseni (regex):", ttk.Entry(f, textvariable=self.var_date_regex),
                "Örn. 2026-09-12 formatı için varsayılan desen yeterlidir. Eşleşme yoksa dosya tarihi kullanılır.")

        # Günlük limit
        self.var_daily_limit = tk.StringVar(value=str(self.cfg.get("gunluk_yukleme_limiti", 6)))
        add_row("Bu Çalıştırmada En Fazla Kaç Video Yüklensin:", ttk.Entry(f, textvariable=self.var_daily_limit),
                "YouTube günlük kotasını aşmamak için önerilen: 6. (Kota aşılırsa yükleme hata verir.)")

        btn_frame = ttk.Frame(f)
        btn_frame.grid(row=row, column=0, columnspan=2, sticky="w", pady=16)
        ttk.Button(btn_frame, text="Ayarları Kaydet", style="Accent.TButton",
                   command=self._save_settings).pack(side="left")
        self.lbl_saved = ttk.Label(btn_frame, text="", style="Dim.TLabel")
        self.lbl_saved.pack(side="left", padx=10)

    def _pick_folder(self):
        path = filedialog.askdirectory(title="Video klasörünü seçin")
        if path:
            self.var_folder.set(path)

    def _pick_secrets(self):
        path = filedialog.askopenfilename(title="client_secret.json dosyasını seçin",
                                           filetypes=[("JSON dosyası", "*.json")])
        if path:
            self.var_secrets.set(path)

    def _collect_settings(self):
        try:
            daily_limit = int(self.var_daily_limit.get())
        except ValueError:
            daily_limit = 6
        return {
            "video_klasoru": self.var_folder.get().strip(),
            "client_secrets_dosyasi": self.var_secrets.get().strip(),
            "ozel_aciklama_metni": self.txt_custom.get("1.0", "end").strip(),
            "gizlilik": self.var_privacy.get(),
            "tarih_deseni": self.var_date_regex.get().strip() or core.DEFAULT_CONFIG["tarih_deseni"],
            "baslik_sablonu": self.var_title_tpl.get().strip() or core.DEFAULT_CONFIG["baslik_sablonu"],
            "aciklama_sablonu": self.txt_desc_tpl.get("1.0", "end").strip() or core.DEFAULT_CONFIG["aciklama_sablonu"],
            "etiketler": self.cfg.get("etiketler", []),
            "gunluk_yukleme_limiti": daily_limit,
        }

    def _save_settings(self):
        self.cfg = self._collect_settings()
        core.save_config(self.cfg)
        self.lbl_saved.config(text="✓ Kaydedildi")
        self.after(2000, lambda: self.lbl_saved.config(text=""))

    # ------------------------------------------------------------------
    # Yükleme sekmesi / Upload tab
    # ------------------------------------------------------------------
    def _build_upload_tab(self):
        f = self.tab_upload
        f.columnconfigure(0, weight=1)
        f.rowconfigure(2, weight=1)

        top = ttk.Frame(f)
        top.grid(row=0, column=0, sticky="ew", pady=(10, 6))
        self.btn_start = ttk.Button(top, text="▶  Yüklemeyi Başlat", style="Accent.TButton",
                                     command=self._start_upload)
        self.btn_start.pack(side="left")
        self.btn_stop = ttk.Button(top, text="■  Durdur", style="Danger.TButton",
                                    command=self._stop_upload, state="disabled")
        self.btn_stop.pack(side="left", padx=8)

        self.progress = ttk.Progressbar(f, mode="indeterminate")
        self.progress.grid(row=1, column=0, sticky="ew", padx=4, pady=(0, 8))

        log_frame = ttk.Frame(f)
        log_frame.grid(row=2, column=0, sticky="nsew", padx=4)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        self.txt_log = tk.Text(log_frame, bg=ENTRY_BG, fg=FG, insertbackground=FG,
                                relief="flat", wrap="word", state="disabled")
        self.txt_log.grid(row=0, column=0, sticky="nsew")
        scroll = ttk.Scrollbar(log_frame, command=self.txt_log.yview)
        scroll.grid(row=0, column=1, sticky="ns")
        self.txt_log.config(yscrollcommand=scroll.set)

    def _append_log(self, text):
        self.txt_log.config(state="normal")
        self.txt_log.insert("end", text + "\n")
        self.txt_log.see("end")
        self.txt_log.config(state="disabled")

    def _start_upload(self):
        self.cfg = self._collect_settings()
        core.save_config(self.cfg)

        if not self.cfg["video_klasoru"] or not os.path.isdir(self.cfg["video_klasoru"]):
            messagebox.showerror("Hata", "Geçerli bir video klasörü seçin (Ayarlar sekmesi).")
            return
        if not self.cfg["client_secrets_dosyasi"] or not os.path.exists(self.cfg["client_secrets_dosyasi"]):
            messagebox.showerror("Hata", "Geçerli bir client_secret.json dosyası seçin (Ayarlar sekmesi).")
            return

        self.stop_flag = False
        self.btn_start.config(state="disabled")
        self.btn_stop.config(state="normal")
        self.progress.start(12)
        self._append_log("=== Yükleme başlatıldı ===")

        self.upload_thread = threading.Thread(target=self._upload_worker, daemon=True)
        self.upload_thread.start()

    def _stop_upload(self):
        self.stop_flag = True
        self._append_log("Durdurma isteği gönderildi, mevcut video tamamlanınca duracak...")

    def _upload_worker(self):
        def log(msg):
            self.log_queue.put(("log", msg))

        def on_item_done(info):
            self.log_queue.put(("item", info))

        def should_stop():
            return self.stop_flag

        try:
            core.run_upload_batch(self.cfg, log=log, on_item_done=on_item_done, should_stop=should_stop)
        except Exception as e:  # noqa: BLE001 - GUI'de kullanıcıya göstermek için genel yakalama
            log(f"BEKLENMEYEN HATA: {e}")
        self.log_queue.put(("done", None))

    def _drain_log_queue(self):
        try:
            while True:
                kind, payload = self.log_queue.get_nowait()
                if kind == "log":
                    self._append_log(payload)
                elif kind == "item":
                    self._add_history_row(payload)
                elif kind == "done":
                    self.progress.stop()
                    self.btn_start.config(state="normal")
                    self.btn_stop.config(state="disabled")
                    self._append_log("=== Bitti ===")
        except queue.Empty:
            pass
        self.after(150, self._drain_log_queue)

    # ------------------------------------------------------------------
    # Geçmiş sekmesi / History tab
    # ------------------------------------------------------------------
    def _build_history_tab(self):
        f = self.tab_history
        f.columnconfigure(0, weight=1)
        f.rowconfigure(1, weight=1)

        top = ttk.Frame(f)
        top.grid(row=0, column=0, sticky="ew", pady=(10, 6))
        ttk.Label(top, text="Daha önce yüklenen / yüklenmeye çalışılan videolar:").pack(side="left")
        ttk.Button(top, text="CSV Dosyasını Aç", command=self._open_csv_folder).pack(side="right")

        columns = ("dosya", "baslik", "tarih", "durum", "link")
        self.tree = ttk.Treeview(f, columns=columns, show="headings")
        headings = {"dosya": "Dosya", "baslik": "Başlık", "tarih": "Tarih",
                    "durum": "Durum", "link": "Link"}
        widths = {"dosya": 160, "baslik": 220, "tarih": 90, "durum": 90, "link": 220}
        for col in columns:
            self.tree.heading(col, text=headings[col])
            self.tree.column(col, width=widths[col], anchor="w")
        self.tree.grid(row=1, column=0, sticky="nsew", padx=4)
        self.tree.bind("<Double-1>", self._open_selected_link)

        vscroll = ttk.Scrollbar(f, command=self.tree.yview)
        vscroll.grid(row=1, column=1, sticky="ns")
        self.tree.config(yscrollcommand=vscroll.set)

        ttk.Label(f, text="Bir linki tarayıcıda açmak için satıra çift tıklayın.",
                  style="Dim.TLabel").grid(row=2, column=0, sticky="w", pady=6)

    def _load_history(self):
        progress = core.load_progress()
        for info in progress.values():
            self._add_history_row(info)

    def _add_history_row(self, info):
        # Aynı dosya tekrar geldiyse eski satırı güncelle
        for iid in self.tree.get_children():
            if self.tree.item(iid, "values")[0] == info.get("dosya"):
                self.tree.delete(iid)
                break
        self.tree.insert("", "end", values=(
            info.get("dosya", ""), info.get("baslik", ""), info.get("tarih", ""),
            info.get("durum", ""), info.get("link", ""),
        ))

    def _open_selected_link(self, _event):
        sel = self.tree.selection()
        if not sel:
            return
        link = self.tree.item(sel[0], "values")[4]
        if link:
            webbrowser.open(link)

    def _open_csv_folder(self):
        folder = os.path.dirname(core.RESULTS_CSV)
        if sys.platform.startswith("win"):
            os.startfile(folder)  # noqa: S606
        elif sys.platform == "darwin":
            os.system(f'open "{folder}"')
        else:
            os.system(f'xdg-open "{folder}"')


if __name__ == "__main__":
    app = App()
    app.mainloop()
