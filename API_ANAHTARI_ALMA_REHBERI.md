# Kendi API Anahtarınızı (client_secret.json) Alma Rehberi

Bu rehber, **her kullanıcının kendi Google hesabıyla, kendi başına** bir
kez yapacağı kurulumu anlatır. Bunu yaptıktan sonra kota (yükleme limiti)
tamamen size ait olur, kimseyle paylaşılmaz. İşlem yaklaşık 5-10 dakika
sürer ve tamamen ücretsizdir — kredi kartı istemez.

Sadece Google hesabınızla tarayıcıdan tıklayarak ilerleyeceksiniz, kod
yazmanıza gerek yok. Adımları sırayla takip edin.

---

## 1. Adım: Google Cloud Console'a girin

1. Tarayıcınızdan **console.cloud.google.com** adresine gidin.
2. Videoları yüklemek istediğiniz Google hesabınızla (Gmail) giriş yapın.
3. İlk kez giriyorsanız kısa bir "hizmet şartları" ekranı çıkabilir,
   ülke seçip kabul edin. Kredi kartı istenmez, korkmayın.

## 2. Adım: Yeni bir proje oluşturun

1. Sayfanın en üstünde, Google logosunun yanında bir proje seçici
   (dropdown) göreceksiniz — muhtemelen "Select a project" yazıyordur.
   Ona tıklayın.
2. Açılan pencerede sağ üstteki **"New Project" (Yeni Proje)** butonuna
   basın.
3. Proje adı olarak istediğiniz bir şey yazın, örneğin:
   `basin-karti-yukleme`
4. "Location" alanını boş/varsayılan bırakabilirsiniz.
5. **Create (Oluştur)** butonuna basın, birkaç saniye bekleyin.
6. Üstteki proje seçiciden az önce oluşturduğunuz projenin **seçili**
   olduğundan emin olun (bazen otomatik seçilmez, elle seçmeniz gerekir).

## 3. Adım: YouTube Data API'yi etkinleştirin

1. Sol üstteki ☰ menüden (ya da arama çubuğundan) **"APIs & Services"**
   → **"Library"** sayfasına gidin.
2. Arama kutusuna `YouTube Data API v3` yazın ve çıkan sonuca tıklayın.
3. Açılan sayfada mavi **"Enable" (Etkinleştir)** butonuna basın.
4. Birkaç saniye içinde etkinleşecek ve otomatik olarak API sayfasına
   yönlendirileceksiniz.

## 4. Adım: OAuth izin ekranını (consent screen) ayarlayın

Bu adım, "bu uygulamayı Google hesabımla kullanmama izin veriyorum"
ekranının nasıl görüneceğini belirler.

1. Sol menüden **"APIs & Services" → "OAuth consent screen"** sayfasına
   gidin.
2. **User Type** olarak **"External"** seçin (aksi halde devam
   edemezsiniz, "Internal" sadece kurumsal Google Workspace hesapları
   içindir) → **Create**.
3. Açılan formda şunları doldurun (diğer alanları boş bırakabilirsiniz):
   - **App name**: istediğiniz bir isim, örn. `Basın Kartı Video Yükleme`
   - **User support email**: kendi e-posta adresiniz
   - **Developer contact information**: yine kendi e-posta adresiniz
4. **Save and Continue** ile ilerleyin.
5. "Scopes" sayfasında hiçbir şey seçmeden **Save and Continue**.
6. **"Test users"** sayfasında **"+ ADD USERS"** butonuna basıp
   **kendi Gmail adresinizi** ekleyin. (Bu çok önemli — eklemezseniz
   program açıldığında giriş yapamazsınız.)
7. **Save and Continue**, sonra özet ekranında **"Back to Dashboard"**.

> Not: Uygulama "Testing" (test) modunda kalacak, bu tamamen normal ve
> yeterlidir — Google'a resmi başvuru/doğrulama göndermenize gerek yok.
> Tek dezavantajı: giriş oturumunuz 7 günde bir düşer, o noktada program
> tarayıcıyı tekrar açıp sizden tekrar giriş yapmanızı ister — bu bir
> hata değildir, normaldir.

## 5. Adım: OAuth Client ID (kimlik bilgisi) oluşturun

1. Sol menüden **"APIs & Services" → "Credentials"** sayfasına gidin.
2. Üstteki **"+ Create Credentials"** butonuna basıp **"OAuth client ID"**
   seçeneğini seçin.
3. **Application type** olarak mutlaka **"Desktop app"** seçin (Web
   application değil!).
4. İsim kısmına istediğiniz bir şey yazabilirsiniz, örn. `Yükleme Programı`.
5. **Create** butonuna basın.
6. Açılan pencerede **"Download JSON"** butonuna basarak dosyayı
   bilgisayarınıza indirin.

## 6. Adım: Dosyayı programa tanıtın

1. İndirdiğiniz dosyanın adı genelde `client_secret_XXXXXX.json` gibi
   uzun bir isimdir. Dosyayı **`client_secret.json`** olarak yeniden
   adlandırın.
2. Bu dosyayı, size verilen program klasörünün içine kopyalayın (ya da
   herhangi bir yere koyup programın **Ayarlar** sekmesinden "Dosya
   Seç..." ile o dosyayı gösterin).
3. Programı açın (`python gui_upload.py`), **Ayarlar** sekmesinde
   `client_secret.json` alanının doğru dosyayı gösterdiğinden emin olun,
   video klasörünüzü ve açıklama metninizi girip **"Ayarları Kaydet"**e
   basın.
4. **Yükleme** sekmesinden **"Yüklemeyi Başlat"**a basın. Tarayıcı
   açılacak, kendi Google hesabınızla giriş yapmanızı isteyecek.

## 7. "Google doğrulamadı" uyarısı çıkarsa

Giriş sırasında **"Google hasn't verified this app"** (Google bu
uygulamayı doğrulamadı) gibi sarı/kırmızı bir uyarı görebilirsiniz.
Bu normaldir — çünkü uygulamayı **siz kendiniz** oluşturdunuz ve resmi
Google incelemesine göndermediniz (buna gerek yok, sadece kendi
hesabınızla kullanacaksınız). Devam etmek için:

1. Uyarı ekranında **"Advanced" (Gelişmiş)** yazısına tıklayın.
2. Altında çıkan **"Go to [uygulama adınız] (unsafe)"** bağlantısına
   tıklayın.
3. Normal izin ekranı açılacak, videolarınızı yükleme iznini onaylayın.

Bu ekranı her gördüğünüzde endişelenmeyin — kendi oluşturduğunuz,
sadece sizin kullandığınız bir uygulama olduğu için güvenlidir.

---

## Sık Sorulanlar

**"Kaç video yükleyebilirim?"**
Kendi projeniz olduğu için günlük kota (10.000 birim) tamamen size ait.
Bir video yükleme ~1600 birim tuttuğundan günde yaklaşık 6 video
yükleyebilirsiniz. Daha fazlası gerekiyorsa ertesi gün devam edin — program
kaldığınız yerden otomatik devam eder.

**"Kredi kartı bilgisi istiyor mu?"**
Hayır, bu adımların hiçbiri ödeme bilgisi istemez.

**"Yanlış bir şey yaptıysam ne olur?"**
Projeyi silip baştan başlayabilirsiniz, hiçbir kalıcı zarar vermez —
kendi Google hesabınız içinde sadece deneme amaçlı bir proje.

---

# Getting Your Own API Key (client_secret.json) — EN Summary

Each person follows this once, with their own Google account, to get
their own YouTube upload quota (not shared with anyone else). Steps:
create a Google Cloud project → enable "YouTube Data API v3" → configure
the OAuth consent screen (External, add yourself as a Test user) →
create an OAuth Client ID of type **Desktop app** → download the JSON,
rename it to `client_secret.json`, and point the app to it in the
Settings tab. The "Google hasn't verified this app" warning is expected
for a self-made testing-mode app — click **Advanced → Go to [app name]
(unsafe)** to proceed; it's safe since you built it yourself. See the
Turkish walkthrough above for the full click-by-click detail.
