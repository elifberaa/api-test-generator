import click
import json
import yaml
import os
import sys
from pathlib import Path
from typing import Dict, Optional
import requests
from datetime import datetime

from .parser import OpenAPIParser
from .generator import TestGenerator


class Colors:
    """Terminal renkleri"""
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    ENDC = '\033[0m'


def print_success(message: str):
    """Başarı mesajı yazdır"""
    click.echo(f"{Colors.GREEN}✓ {message}{Colors.ENDC}")

def print_info(message: str):
    """Bilgi mesajı yazdır"""
    click.echo(f"{Colors.BLUE}ℹ {message}{Colors.ENDC}")

def print_warning(message: str):
    """Uyarı mesajı yazdır"""
    click.echo(f"{Colors.YELLOW}⚠ {message}{Colors.ENDC}")

def print_error(message: str):
    """Hata mesajı yazdır"""
    click.echo(f"{Colors.RED}✗ {message}{Colors.ENDC}")


def load_openapi_spec(source: str) -> Dict:
    """OpenAPI belirtimini yükle (dosya veya URL)"""
    
    if source.startswith(('http://', 'https://')):
        print_info(f"URL'den OpenAPI belirtimi indiriliyor: {source}")
        try:
            response = requests.get(source, timeout=30)
            response.raise_for_status()
            
            content_type = response.headers.get('content-type', '').lower()
            
            if 'yaml' in content_type or source.endswith(('.yaml', '.yml')):
                return yaml.safe_load(response.text)
            else:
                return response.json()
                
        except requests.exceptions.RequestException as e:
            print_error(f"URL'den belirtim yüklenemedi: {e}")
            sys.exit(1)
        except (json.JSONDecodeError, yaml.YAMLError) as e:
            print_error(f"Belirtim formatı geçersiz: {e}")
            sys.exit(1)
    
    else:
        # Dosya yolu
        file_path = Path(source)
        
        if not file_path.exists():
            print_error(f"Dosya bulunamadı: {source}")
            sys.exit(1)
        
        print_info(f"OpenAPI belirtimi dosyadan okunuyor: {source}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if file_path.suffix.lower() in ['.yaml', '.yml']:
                return yaml.safe_load(content)
            else:
                return json.loads(content)
                
        except (json.JSONDecodeError, yaml.YAMLError) as e:
            print_error(f"Belirtim formatı geçersiz: {e}")
            sys.exit(1)
        except Exception as e:
            print_error(f"Dosya okunurken hata: {e}")
            sys.exit(1)


def ensure_test_directory(output_dir: str) -> Path:
    """Test dizinini oluştur"""
    test_dir = Path(output_dir)
    test_dir.mkdir(parents=True, exist_ok=True)
    
    # __init__.py dosyasını oluştur
    init_file = test_dir / "__init__.py"
    if not init_file.exists():
        init_file.write_text("# Auto-generated test package\n")
    
    return test_dir


def save_test_file(test_dir: Path, filename: str, content: str, force: bool = False):
    """Test dosyasını kaydet"""
    file_path = test_dir / filename
    
    if file_path.exists() and not force:
        print_warning(f"Dosya zaten var: {filename}. --force ile üzerine yazabilirsiniz.")
        return False
    
    try:
        file_path.write_text(content, encoding='utf-8')
        print_success(f"Test dosyası oluşturuldu: {filename}")
        return True
    except Exception as e:
        print_error(f"Dosya kaydedilirken hata: {e}")
        return False


def generate_config_file(output_dir: str, base_url: str):
    """Konfigürasyon dosyası oluştur"""
    config_content = f'''# API Test Configuration
import os

class Config:
    """Test konfigürasyonu"""
    
    BASE_URL = "{base_url}"
    
    # Timeout ayarları (saniye)
    REQUEST_TIMEOUT = 30
    
    # Retry ayarları
    MAX_RETRIES = 3
    RETRY_DELAY = 1
    
    # Log ayarları
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    # Authentication (gerekirse)
    API_KEY = os.getenv('API_KEY', '')
    BEARER_TOKEN = os.getenv('BEARER_TOKEN', '')
    
    # Test verileri
    TEST_USER_EMAIL = os.getenv('TEST_USER_EMAIL', 'test@example.com')
    TEST_USER_PASSWORD = os.getenv('TEST_USER_PASSWORD', 'test123')

config = Config()
'''
    
    config_dir = Path(output_dir) / "config"
    config_dir.mkdir(exist_ok=True)
    
    config_file = config_dir / "test_config.py"
    config_file.write_text(config_content)
    print_success("Konfigürasyon dosyası oluşturuldu: config/test_config.py")


def generate_pytest_ini(output_dir: str):
    """pytest konfigürasyon dosyası oluştur"""
    ini_content = '''[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --tb=short
    --strict-markers
    --disable-warnings
markers =
    smoke: quick smoke tests
    integration: integration tests
    unit: unit tests
    slow: slow running tests
'''
    
    ini_file = Path(output_dir) / "pytest.ini"
    ini_file.write_text(ini_content)
    print_success("pytest konfigürasyon dosyası oluşturuldu: pytest.ini")


@click.command()
@click.argument('source', required=True)
@click.option('--output', '-o', default='tests', help='Çıktı dizini (varsayılan: tests)')
@click.option('--base-url', '-u', default='http://localhost:8000', help='API base URL')
@click.option('--tag', '-t', help='Sadece belirli tag için test üret')
@click.option('--force', '-f', is_flag=True, help='Mevcut dosyaların üzerine yaz')
@click.option('--config-only', is_flag=True, help='Sadece konfigürasyon dosyalarını oluştur')
@click.version_option(version='1.0.0', prog_name='API Test Generator')
def generate(source: str, output: str, base_url: str, tag: Optional[str], force: bool, config_only: bool):
    """
    OpenAPI/Swagger belirtiminden otomatik test kodları üret.
    
    SOURCE: OpenAPI JSON/YAML dosyası veya URL
    
    Örnek kullanım:
    \b
        api-test-generator openapi.json
        api-test-generator https://api.example.com/openapi.json --base-url https://api.example.com
        api-test-generator openapi.yaml --tag users --output tests/users
    """
    
    print_info(f"API Test Generator başlatılıyor...")
    print_info(f"Kaynak: {source}")
    print_info(f"Çıktı dizini: {output}")
    print_info(f"Base URL: {base_url}")
    
    try:
        # Konfigürasyon dosyalarını oluştur
        if config_only:
            generate_config_file(output, base_url)
            generate_pytest_ini(output)
            print_success("Konfigürasyon dosyaları başarıyla oluşturuldu!")
            return
        
        # OpenAPI belirtimini yükle
        spec = load_openapi_spec(source)
        print_success("OpenAPI belirtimi başarıyla yüklendi")
        
        # Parser'ı oluştur
        print_info("API belirtimi ayrıştırılıyor...")
        parser = OpenAPIParser(spec)
        
        print_success(f"Toplam {len(parser.endpoints)} endpoint bulundu")
        
        # Generator'ı oluştur
        generator = TestGenerator(parser)
        
        # Test dizinini oluştur
        test_dir = ensure_test_directory(output)
        
        # Test dosyalarını üret
        test_files_created = 0
        
        if tag:
            # Sadece belirli tag için test üret
            print_info(f"'{tag}' tag'i için testler üretiliyor...")
            test_content = generator.generate_test_file_by_tag(tag, base_url)
            
            if test_content:
                filename = f"test_{tag}_endpoints.py"
                if save_test_file(test_dir, filename, test_content, force):
                    test_files_created += 1
            else:
                print_warning(f"'{tag}' tag'ine sahip endpoint bulunamadı")
        
        else:
            # Tüm testleri üret
            print_info("Tüm endpoint'ler için testler üretiliyor...")
            test_files = generator.generate_all_tests(base_url)
            
            for filename, content in test_files.items():
                if save_test_file(test_dir, filename, content, force):
                    test_files_created += 1
        
        # Konfigürasyon dosyalarını oluştur
        generate_config_file(output, base_url)
        generate_pytest_ini(output)
        
        # Özet bilgiler
        print("\n" + "="*50)
        print_success(f"Test üretimi tamamlandı!")
        print_info(f"Oluşturulan test dosyaları: {test_files_created}")
        print_info(f"Toplam endpoint: {len(parser.endpoints)}")
        
        if tag:
            tag_endpoints = len(parser.get_endpoints_by_tag(tag))
            print_info(f"'{tag}' tag'ine sahip endpoint'ler: {tag_endpoints}")
        
        print("\n" + "Testleri çalıştırmak için:")
        print(f"  cd {os.path.dirname(test_dir.absolute())}")
        print("  python -m pytest")
        print("  # veya")
        print("  pytest -v")
        
        print("\n" + "Diğer kullanışlı komutlar:")
        print("  pytest -v --tb=short        # Daha az detaylı hata çıktısı")
        print("  pytest -k 'test_get'        # Sadece GET testleri")
        print("  pytest -m smoke             # Smoke testleri")
        print("  pytest --html=report.html   # HTML raporu oluştur")
        
    except KeyboardInterrupt:
        print_warning("İşlem kullanıcı tarafından iptal edildi.")
        sys.exit(1)
    except Exception as e:
        print_error(f"Beklenmeyen hata: {e}")
        sys.exit(1)


@click.group()
@click.version_option(version='1.0.0', prog_name='API Test Generator')
def cli():
    """API Test Generator - OpenAPI'dan otomatik test kodları üret"""
    pass


@cli.command()
@click.argument('source')
@click.option('--output', '-o', default='tests', help='Çıktı dizini')
@click.option('--base-url', '-u', default='http://localhost:8000', help='API base URL')
@click.option('--tag', '-t', help='Sadece belirli tag için test üret')
@click.option('--force', '-f', is_flag=True, help='Mevcut dosyaların üzerine yaz')
def create(source: str, output: str, base_url: str, tag: Optional[str], force: bool):
    """Yeni testler oluştur"""
    # generate fonksiyonunun içeriğini doğrudan kullan
    print_info(f"API Test Generator başlatılıyor...")
    print_info(f"Kaynak: {source}")
    print_info(f"Çıktı dizini: {output}")
    print_info(f"Base URL: {base_url}")
    
    try:
        # OpenAPI belirtimini yükle
        spec = load_openapi_spec(source)
        print_success("OpenAPI belirtimi başarıyla yüklendi")
        
        # Parser'ı oluştur
        print_info("API belirtimi ayrıştırılıyor...")
        parser = OpenAPIParser(spec)
        
        print_success(f"Toplam {len(parser.endpoints)} endpoint bulundu")
        
        # Generator'ı oluştur
        generator = TestGenerator(parser)
        
        # Test dizinini oluştur
        test_dir = ensure_test_directory(output)
        
        # Test dosyalarını üret
        test_files_created = 0
        
        if tag:
            # Sadece belirli tag için test üret
            print_info(f"'{tag}' tag'i için testler üretiliyor...")
            test_content = generator.generate_test_file_by_tag(tag, base_url)
            
            if test_content:
                filename = f"test_{tag}_endpoints.py"
                if save_test_file(test_dir, filename, test_content, force):
                    test_files_created += 1
            else:
                print_warning(f"'{tag}' tag'ine sahip endpoint bulunamadı")
        
        else:
            # Tüm testleri üret
            print_info("Tüm endpoint'ler için testler üretiliyor...")
            test_files = generator.generate_all_tests(base_url)
            
            for filename, content in test_files.items():
                if save_test_file(test_dir, filename, content, force):
                    test_files_created += 1
        
        # Konfigürasyon dosyalarını oluştur
        generate_config_file(output, base_url)
        generate_pytest_ini(output)
        
        # Özet bilgiler
        print("\n" + "="*50)
        print_success(f"Test üretimi tamamlandı!")
        print_info(f"Oluşturulan test dosyaları: {test_files_created}")
        print_info(f"Toplam endpoint: {len(parser.endpoints)}")
        
        if tag:
            tag_endpoints = len(parser.get_endpoints_by_tag(tag))
            print_info(f"'{tag}' tag'ine sahip endpoint'ler: {tag_endpoints}")
        
        print("\n" + "Testleri çalıştırmak için:")
        print(f"  cd {os.path.dirname(test_dir.absolute())}")
        print("  python -m pytest")
        print("  # veya")
        print("  pytest -v")
        
        print("\n" + "Diğer kullanışlı komutlar:")
        print("  pytest -v --tb=short        # Daha az detaylı hata çıktısı")
        print("  pytest -k 'test_get'        # Sadece GET testleri")
        print("  pytest -m smoke             # Smoke testleri")
        print("  pytest --html=report.html   # HTML raporu oluştur")
        
    except KeyboardInterrupt:
        print_warning("İşlem kullanıcı tarafından iptal edildi.")
        sys.exit(1)
    except Exception as e:
        print_error(f"Beklenmeyen hata: {e}")
        sys.exit(1)


@cli.command()
@click.option('--output', '-o', default='.', help='Çıktı dizini')
def init(output: str):
    """Yeni bir test projesi başlat"""
    print_info("Yeni test projesi başlatılıyor...")
    
    # Proje dizinini oluştur
    project_dir = Path(output)
    project_dir.mkdir(parents=True, exist_ok=True)
    
    # Temel dizin yapısı
    (project_dir / 'tests').mkdir(exist_ok=True)
    (project_dir / 'config').mkdir(exist_ok=True)
    (project_dir / 'data').mkdir(exist_ok=True)
    (project_dir / 'reports').mkdir(exist_ok=True)
    
    # requirements.txt oluştur
    requirements = """# API Test Generator Requirements
requests>=2.31.0
pytest>=7.4.0
pytest-asyncio>=0.21.0
pytest-html>=4.1.0
pytest-xdist>=3.5.0
pydantic>=2.5.0
httpx>=0.25.0
jinja2>=3.1.0
pyyaml>=6.0.1
click>=8.1.0
rich>=13.7.0
jsonschema>=4.20.0
faker>=20.1.0
python-dotenv>=1.0.0
"""
    
    (project_dir / 'requirements.txt').write_text(requirements)
    
    # README oluştur
    readme = """# API Test Project

Bu proje API Test Generator ile otomatik olarak oluşturulmuştur.

## Kurulum

```bash
pip install -r requirements.txt
```

## Kullanım

```bash
# OpenAPI dosyasından test oluştur
api-test-generator create openapi.json --base-url https://api.example.com

# Sadece belirli tag'ler için test oluştur
api-test-generator create openapi.json --tag users --base-url https://api.example.com

# Testleri çalıştır
pytest -v
```

## Yapı

- `tests/` - Otomatik oluşturulan test dosyaları
- `config/` - Test konfigürasyonları
- `data/` - Test veri dosyaları
- `reports/` - Test raporları
"""
    
    (project_dir / 'README.md').write_text(readme)
    
    print_success(f"Proje başlatıldı: {project_dir.absolute()}")
    print_info("Şimdi 'api-test-generator create' komutuyla testler oluşturabilirsiniz.")


# Ana CLI komutunu ekle
cli.add_command(generate)

if __name__ == '__main__':
    cli()