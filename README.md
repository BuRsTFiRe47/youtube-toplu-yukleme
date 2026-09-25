# YouTube Toplu Video Yükleme Aracı (Arayüzlü)

Basın kartı başvurusu için çok sayıda videoyu YouTube'a yüklerken her birine
otomatik başlık/tarih/açıklama ekleyen, **karanlık temalı**, arayüzlü bir
araç. Program kapatılıp tekrar açıldığında daha önce yüklenen videoları
otomatik hatırlar ve kaldığı yerden devam eder.

## Özellikler

- **Ayarlar sekmesi**: video klasörü, açıklamaya eklenecek sabit metin,
  gizlilik ayarı, başlık/açıklama şablonları — hepsi arayüzden, kod
  değiştirmeye gerek yok.
- **Yükleme sekmesi**: tek tuşla başlat/durdur, canlı ilerleme günlüğü.
- **Geçmiş sekmesi**: daha önce yüklenen (veya hata veren) her video bir
  tabloda; linke çift tıklayınca tarayıcıda açılır.
- **Kaldığı yerden devam**: `progress.json` dosyasında hangi videoların
  yüklendiği kayıtlıdır; programı kapatıp açsanız da, bilgisayarı yeniden
  başlatsanız da zaten yüklenenler tekrar yüklenmez.

## Her kullanıcı kendi hesabına, kendi API anahtarıyla yükler

Bu sürümde **kota paylaşımı yok**: her kişi kendi Google hesabıyla kendi
Google Cloud projesini oluşturur (`client_secret.json`), böylece günlük
yükleme kotası (varsayılan ~6 video/gün) tamamen kendisine ait olur,
başka kimseyi etkilemez / kimseden etkilenmez. Bu kurulum kişi başına
tek seferlik ve ~5-10 dakika sürer; adım adım, ekran ekran anlatan
rehber için bkz. **[API_ANAHTARI_ALMA_REHBERI.md](API_ANAHTARI_ALMA_REHBERI.md)**
— bu dosyayı doğrudan 50 kişiye repo ile birlikte iletebilirsiniz.

## Kurulum (GitHub'dan)

```bash
git clone https://github.com/BuRsTFiRe47/youtube-toplu-yukleme.git
cd youtube-toplu-yukleme
pip install -r requirements.txt
```

> Not: Python kurulumunda (özellikle Windows'ta) "tcl/tk" bileşeninin
> seçili olduğundan emin olun — arayüz (tkinter) bunu kullanır ve
> python.org'dan indirilen standart kurulumda varsayılan olarak gelir.

### Her kullanıcı ne yapacak?

1. Repoyu indirir / klonlar, `pip install -r requirements.txt` çalıştırır.
2. **[API_ANAHTARI_ALMA_REHBERI.md](API_ANAHTARI_ALMA_REHBERI.md)**
   dosyasındaki adımları takip ederek **kendi** `client_secret.json`
   dosyasını oluşturur (yaklaşık 5-10 dakika, tek seferlik).
3. `python gui_upload.py` ile programı açar.
4. **Ayarlar** sekmesinde `client_secret.json` dosyasını, video
   klasörünü, açıklama metnini ve gizlilik ayarını girip "Ayarları
   Kaydet"e basar.
5. **Yükleme** sekmesinde "Yüklemeyi Başlat"a basar — ilk seferde
   tarayıcı açılır, kendi Google hesabıyla giriş yapıp izin verir
   ("Google doğrulamadı" uyarısı çıkarsa rehberdeki 7. adıma bakın,
   normaldir).
6. **Geçmiş** sekmesinden kendi yüklediği video linklerini görür /
   kopyalar.

## Dosya adından tarih çıkarma

Video dosya adında `2026-09-12` gibi bir tarih varsa otomatik yakalanır.
Farklı format kullanıyorsanız Ayarlar sekmesindeki "Dosya Adından Tarih
Deseni (regex)" alanını değiştirin. Tarih bulunamazsa dosyanın değişiklik
tarihi kullanılır.

## Sonuçlar nerede?

- `yuklenen_videolar.csv`: tüm video linkleri, başlıkları, tarihleri.
- `progress.json`: dahili ilerleme kaydı (silinirse geçmiş / kaldığı yerden
  devam bilgisi kaybolur).

## Repo yapısı

```
youtube-toplu-yukleme/
├── gui_upload.py                    # Arayüzlü uygulama (önerilen)
├── upload_cli.py                     # Komut satırı sürümü (isteğe bağlı)
├── core.py                            # Ortak yükleme mantığı
├── config.example.json                # Ayar şablonu (ilk çalıştırmada config.json otomatik oluşur)
├── API_ANAHTARI_ALMA_REHBERI.md        # Her kullanıcının kendi API anahtarını alma rehberi
├── requirements.txt
└── .gitignore                          # client_secret.json, token.pickle vb. repoya girmez
```

---

# YouTube Bulk Video Uploader — GUI edition (EN)

A dark-themed desktop GUI for uploading many videos to YouTube with
auto-generated titles/dates and a fixed custom description text appended
to each one. Remembers what's already been uploaded across restarts
(Settings / Upload / History tabs).

Each person creates their **own** Google Cloud project and
`client_secret.json` (see `API_ANAHTARI_ALMA_REHBERI.md` for a detailed,
click-by-click walkthrough, with an English summary at the bottom of
that file) — so nobody shares a quota, and each person's daily upload
limit (~6 videos/day by default) is entirely their own.

Setup and usage steps are otherwise the same as the Turkish section
above — clone the repo, `pip install -r requirements.txt`, follow the
guide to get your own `client_secret.json`, run `python gui_upload.py`.
