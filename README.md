# 🚀 API Test Generator

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**OpenAPI/Swagger belirtimlerinden otomatik API test kodları üretme aracı**

API Test Generator, OpenAPI 3.x ve Swagger 2.0 belirtimlerini kullanarak otomatik olarak pytest tabanlı API test kodları üretir. Manuel test yazma sürecini otomatikleştirir, zamandan tasarruf sağlar ve API'nizin güvenilirliğini artırır.

## ✨ Özellikler

- 🔄 **OpenAPI 3.x & Swagger 2.0 Desteği** - Modern ve legacy API belirtimlerini destekler
- 🎯 **Otomatik Test Üretimi** - Endpoint'ler için kapsamlı test senaryoları oluşturur
- 🔧 **Esnek Konfigürasyon** - Base URL, timeout, authentication gibi ayarlar
- 📊 **Çoklu Format Desteği** - JSON ve YAML dosyalarını okuyabilir
- 🌐 **URL'den Yükleme** - API belirtimlerini doğrudan URL'den indirebilir
- 🏷️ **Etiket Bazlı Filtreleme** - Sadece belirli endpoint grupları için test üret
- ⚡ **Hızlı Kurulum** - Tek komutla kurulum ve kullanım
- 🎨 **Renkli CLI** - Kullanıcı dostu terminal arayüzü
- 📈 **Response Doğrulama** - Status code, content-type, response time kontrolleri
- 🔒 **Tip Güvenliği** - Pydantic ile güçlü veri modelleme

## 📦 Kurulum

### Pip ile Kurulum (Önerilen)

```bash
pip install api-test-generator
```

### Kaynak Kodundan Kurulum

```bash
git clone https://github.com/openclaw/api-test-generator.git
cd api-test-generator
pip install -e .
```

### Gereksinimler

- Python 3.8+
- pip paket yöneticisi

## 🚀 Hızlı Başlangıç

### 1. Basit Kullanım

OpenAPI dosyanızdan otomatik testler oluşturun:

```bash
# Yerel dosyadan
api-test-generator create openapi.json

# YAML dosyasından
api-test-generator create openapi.yaml

# URL'den
api-test-generator create https://api.example.com/openapi.json
```

### 2. API Base URL ile Kullanım

Testlerin hitap edeceği API adresini belirtin:

```bash
api-test-generator create openapi.json --base-url https://api.example.com
```

### 3. Sadece Belirli Endpoint'ler için Test Üretme

Belirli bir etikete (tag) sahip endpoint'ler için test oluşturun:

```bash
api-test-generator create openapi.json --tag users
api-test-generator create openapi.json --tag products --base-url https://api.example.com
```

### 4. Yeni Proje Başlatma

Boş bir test projesi oluşturun:

```bash
api-test-generator init my-api-tests
cd my-api-tests
api-test-generator create ../openapi.json --base-url https://api.example.com
```

## 📋 CLI Komutları

### Temel Komutlar

#### `create` - Test Oluştur
```bash
api-test-generator create SOURCE [OPTIONS]
```

**Parametreler:**
- `SOURCE`: OpenAPI JSON/YAML dosyası veya URL

**Seçenekler:**
- `--output, -o`: Çıktı dizini (varsayılan: tests)
- `--base-url, -u`: API base URL (varsayılan: http://localhost:8000)
- `--tag, -t`: Sadece belirli tag için test üret
- `--force, -f`: Mevcut dosyaların üzerine yaz

**Örnekler:**
```bash
api-test-generator create openapi.json
api-test-generator create openapi.yaml --output tests/api
api-test-generator create https://api.example.com/openapi.json --base-url https://api.example.com --tag users
```

#### `init` - Proje Başlat
```bash
api-test-generator init [OPTIONS] [DIRECTORY]
```

**Seçenekler:**
- `--output, -o`: Proje dizini (varsayılan: .)

**Örnekler:**
```bash
api-test-generator init
api-test-generator init my-api-project
```

### Gelişmiş Kullanım

#### Farklı Çıktı Dizinleri
```bash
# Testleri farklı dizine kaydet
api-test-generator create openapi.json --output integration-tests

# Organize klasör yapısı
api-test-generator create openapi.json --output tests/integration
```

#### Üzerine Yazma
```bash
# Mevcut testlerin üzerine yaz
api-test-generator create openapi.json --force
```

#### Çoklu Etiket Kullanımı
```bash
# Users ve auth tag'leri için ayrı ayrı testler
api-test-generator create openapi.json --tag users --output tests/users
api-test-generator create openapi.json --tag auth --output tests/auth
```

## 🏗️ Oluşturulan Proje Yapısı

```
my-api-tests/
├── tests/                    # Otomatik oluşturulan test dosyaları
│   ├── test_get_users.py
│   ├── test_post_users.py
│   ├── test_get_products_id.py
│   └── __init__.py
├── config/                   # Konfigürasyon dosyaları
│   └── test_config.py       # API ayarları, timeout'lar
├── data/                     # Test veri dosyaları
├── reports/                  # Test raporları
├── pytest.ini               # pytest konfigürasyonu
├── requirements.txt         # Bağımlılıklar
└── README.md               # Proje dökümantasyonu
```

## 🧪 Testleri Çalıştırma

### Temel Kullanım
```bash
# Tüm testleri çalıştır
pytest

# Detaylı çıktı ile
pytest -v

# Sadece GET testleri
pytest -k "test_get"

# Belirli bir test dosyası
pytest tests/test_get_users.py
```

### Gelişmiş Seçenekler
```bash
# HTML raporu oluştur
pytest --html=reports/test_report.html

# Paralel test çalıştırma
pytest -n auto

# Smoke testleri
pytest -m smoke

# Daha az detaylı hata çıktısı
pytest --tb=short
```

## ⚙️ Konfigürasyon

### Environment Değişkenleri

```bash
export API_KEY="your-api-key"
export BEARER_TOKEN="your-bearer-token"
export TEST_USER_EMAIL="test@example.com"
export TEST_USER_PASSWORD="test123"
export LOG_LEVEL="DEBUG"
```

### Config Dosyası

`config/test_config.py` dosyasında ayarları özelleştirebilirsiniz:

```python
class Config:
    BASE_URL = "https://api.example.com"
    REQUEST_TIMEOUT = 30
    MAX_RETRIES = 3
    LOG_LEVEL = "INFO"
```

## 🔧 Örnek OpenAPI Belirtimi

```yaml
openapi: 3.0.0
info:
  title: Kullanıcı API'si
  version: 1.0.0
paths:
  /users:
    get:
      summary: Tüm kullanıcıları listele
      tags: [users]
      parameters:
        - name: limit
          in: query
          schema:
            type: integer
            default: 10
      responses:
        '200':
          description: Başarılı
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/User'
    
  /users/{id}:
    get:
      summary: Kullanıcı detayını getir
      tags: [users]
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: integer
      responses:
        '200':
          description: Başarılı
        '404':
          description: Kullanıcı bulunamadı
```

Bu belirtimden şu test kodu otomatik olarak üretilir:

```python
import pytest
import requests

class TestUsersGet:
    """Tests for GET /users"""
    
    base_url = "http://localhost:8000"
    
    def test_get_users(self, limit: int = 10):
        """GET /users - Basic test"""
        
        url = f"{self.base_url}/users"
        
        # Query parametreleri
        params = {
            "limit": 10,
        }
        
        # HTTP isteği gönder
        response = requests.get(url, params=params)
        
        # Temel doğrulamalar
        assert response.status_code in [200]
        
        # JSON response kontrolü
        assert response.headers.get('content-type', '').startswith('application/json')
        json_data = response.json()
        assert isinstance(json_data, (dict, list))
        
        # Response süresi kontrolü
        assert response.elapsed.total_seconds() < 30
        
        print(f"✓ GET /users - Status: {response.status_code}")
        
        return response
```

## 🛠️ Geliştirme

### Kurulum Geliştirme Ortamı

```bash
git clone https://github.com/openclaw/api-test-generator.git
cd api-test-generator
pip install -e .[dev]
```

### Test Etme

```bash
# Birim testleri
pytest tests/

# Kod kalitesi
flake8 src/
black src/
mypy src/
```

## 🐛 Sorun Giderme

### Yaygın Hatalar

#### "OpenAPI belirtimi yüklenemedi"
- URL'nin doğru olduğundan emin olun
- Dosya yolunun doğru olduğunu kontrol edin
- Dosya izinlerini kontrol edin

#### "Mevcut dosyaların üzerine yazılamıyor"
- `--force` bayrağını kullanın
- Dosya izinlerini kontrol edin

#### "Testler çalışmıyor"
- Base URL'nin doğru olduğunu kontrol edin
- API'nin çalıştığından emin olun
- Network bağlantısını kontrol edin

### Debug Modu

```bash
export LOG_LEVEL=DEBUG
api-test-generator create openapi.json
```

## 🤝 Katkıda Bulunma

Katkılarınız memnuniyetle karşılanır! Lütfen:

1. Bu depoyu fork edin
2. Yeni bir dal oluşturun (`git checkout -b feature/amazing-feature`)
3. Değişikliklerinizi commit edin (`git commit -m 'Add amazing feature'`)
4. Dalınıza push edin (`git push origin feature/amazing-feature`)
5. Bir Pull Request açın

## 📄 Lisans

Bu proje MIT lisansı altında lisanslanmıştır - detaylar için [LICENSE](LICENSE) dosyasına bakın.

## 🙏 Teşekkürler

- [OpenAPI Initiative](https://www.openapis.org/) - OpenAPI belirtimi için
- [pytest](https://pytest.org/) - Harika test framework'ü için
- [Pydantic](https://pydantic-docs.helpmanual.io/) - Tip doğrulama ve veri modelleme için
- [Click](https://click.palletsprojects.com/) - CLI framework'ü için



---

**API Test Generator** - OpenAPI'dan test kodlarına, otomatik ve hatasız! 🤖✨
