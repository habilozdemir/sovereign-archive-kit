# Sovereign Archive Kit (Türkçe Kılavuz)

**Medium, Mastodon, Nostr ve yerel makale/PDF koleksiyonlarını sıfır dış bağımlılıkla (yalnızca Python standart kütüphanesiyle) temiz, kriptografik SHA-256 mühürlü ve ömür boyu kalıcı dijital arşivlere dönüştüren açık kaynak araç seti ve 4 katmanlı kalıcılık protokolü.**

> **[Click here for English Documentation (README.md)](README.md)**

## Hızlı Kullanım

### Klonlamadan Tek Satırda Çalıştır

```bash
curl -sL https://raw.githubusercontent.com/habilozdemir/sovereign-archive-kit/main/archive_kit.py -o archive_kit.py && python3 archive_kit.py --help
```

```bash
# 1. Medium yedek paketini (.zip) temiz ve SHA-256 mühürlü arşive dönüştür (taslakları otomatik ayıklar)
python3 archive_kit.py medium ~/Downloads/medium-export.zip -o ./medium-archive

# 2. Mastodon yedek paketini (.tar.gz veya .zip) temiz arşive dönüştür (özel mesajları otomatik ayıklar)
python3 archive_kit.py mastodon ~/Downloads/archive-mastodon.tar.gz -o ./mastodon-archive

# 3. Nostr yedek dosyasını (.json) doğrulanmış arşive dönüştür
python3 archive_kit.py nostr ~/Downloads/nostr-events.json -o ./nostr-archive

# 4. Bilgisayarındaki herhangi bir PDF veya Markdown klasörünü MANIFEST.sha256 ile mühürle
python3 archive_kit.py seal ./yazilarim

# 5. Arşiv bütünlüğünü macOS, Linux veya Windows üzerinde istediğin zaman doğrula
python3 archive_kit.py verify ./yazilarim
```

## 4 Katmanlı Kalıcılık Protokolü

1. **GitHub Salt Okunur Kasa:** Mühürlenen klasörü herkese açık bir GitHub deposuna yükleyin ve **Settings -> Danger Zone -> Archive this repository** ile salt okunur kilitleyin.
2. **Software Heritage:** Depo adresinizi [Software Heritage Save Code Now](https://archive.softwareheritage.org/save/) sayfasına göndererek küresel akademik arşive kaydedin.
3. **Wayback Machine:** Depo adresinizi [Wayback Machine Save Page Now](https://web.archive.org/save/) sayfasına gönderin.
4. **Merkeziyetsiz Zaman Damgası (Nostr):** `MANIFEST.sha256` dosyanızın **Master SHA-256** özetini Nostr rölelerinde paylaşarak değiştirilemez varlık kanıtı oluşturun.
