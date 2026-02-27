from typing import Dict, List, Optional, Any
import json
from datetime import datetime

from .parser import OpenAPIParser, Endpoint, HTTPMethod, Parameter, ParameterType, RequestBody


class TestGenerator:
    """API endpoint'leri için otomatik test kodu üretici"""
    
    def __init__(self, parser: OpenAPIParser):
        self.parser = parser
    
    def generate_test_class(self, endpoint: Endpoint, base_url: str = "http://localhost:8000") -> str:
        """Tek bir endpoint için test sınıfı üret"""
        
        class_name = self._generate_class_name(endpoint)
        test_methods = self._generate_test_methods(endpoint, base_url)
        
        code_parts = []
        
        # Importlar
        code_parts.append("import pytest")
        code_parts.append("import requests")
        code_parts.append("import json")
        code_parts.append("from typing import Dict, Any, Optional")
        code_parts.append("from datetime import datetime")
        code_parts.append("")
        
        # Sınıf tanımı
        code_parts.append(f"class Test{class_name}:")
        code_parts.append(f'    """Tests for {endpoint.method.value.upper()} {endpoint.path}"""')
        code_parts.append("")
        code_parts.append(f'    base_url = "{base_url.rstrip("/")}"')
        code_parts.append("")
        
        # Test metodları
        for method_code in test_methods:
            code_parts.extend(method_code)
            code_parts.append("")
        
        return "\n".join(code_parts)
    
    def generate_all_tests(self, base_url: str = "http://localhost:8000") -> Dict[str, str]:
        """Tüm endpoint'ler için test kodları üret"""
        test_files = {}
        
        for endpoint in self.parser.endpoints:
            test_code = self.generate_test_class(endpoint, base_url)
            file_name = f"test_{endpoint.method.value}_{self._generate_file_name(endpoint.path)}.py"
            test_files[file_name] = test_code
        
        return test_files
    
    def generate_test_file_by_tag(self, tag: str, base_url: str = "http://localhost:8000") -> str:
        """Belirli bir tag'e sahip endpoint'ler için test dosyası üret"""
        endpoints = self.parser.get_endpoints_by_tag(tag)
        
        if not endpoints:
            return ""
        
        code_parts = []
        
        # Importlar
        code_parts.append("import pytest")
        code_parts.append("import requests")
        code_parts.append("import json")
        code_parts.append("from typing import Dict, Any, Optional")
        code_parts.append("from datetime import datetime")
        code_parts.append("")
        
        # Her endpoint için test sınıfı
        for endpoint in endpoints:
            test_methods = self._generate_test_methods(endpoint, base_url)
            
            class_name = self._generate_class_name(endpoint)
            code_parts.append(f"class Test{class_name}:")
            code_parts.append(f'    """Tests for {endpoint.method.value.upper()} {endpoint.path}"""')
            code_parts.append("")
            code_parts.append(f'    base_url = "{base_url.rstrip("/")}"')
            code_parts.append("")
            
            for method_code in test_methods:
                code_parts.extend(method_code)
                code_parts.append("")
        
        return "\n".join(code_parts)
    
    def _generate_test_methods(self, endpoint: Endpoint, base_url: str) -> List[List[str]]:
        """Endpoint için test metodları oluştur"""
        methods = []
        
        # Ana test metodu
        main_method = self._create_main_test_method(endpoint, base_url)
        methods.append(main_method)
        
        # Parametre varyasyonları için ek testler
        param_methods = self._create_parameter_variation_tests(endpoint, base_url)
        methods.extend(param_methods)
        
        return methods
    
    def _create_main_test_method(self, endpoint: Endpoint, base_url: str) -> List[str]:
        """Ana test metodunu oluştur"""
        lines = []
        
        # Parametreleri ayır
        query_params = [p for p in endpoint.parameters if p.type == ParameterType.QUERY]
        path_params = [p for p in endpoint.parameters if p.type == ParameterType.PATH]
        header_params = [p for p in endpoint.parameters if p.type == ParameterType.HEADER]
        
        # Metod imzası - Pytest parametre almaz!
        lines.append(f"    def test_{endpoint.method.value}_{self._generate_method_suffix(endpoint.path)}(self):")
        lines.append(f'        """{endpoint.method.value.upper()} {endpoint.path} - Basic test"""')
        lines.append("")
        
        # Path parametreleri varsa, örnek değerler oluştur
        if path_params:
            lines.append("        # Path parametreleri için örnek değerler")
            for param in path_params:
                example_val = self._get_example_value(param).strip('"')
                lines.append(f"        {param.name} = {example_val}")
            lines.append("")
        
        # Query parametreleri varsa, örnek değerler oluştur
        if query_params:
            lines.append("        # Query parametreleri için örnek değerler")
            for param in query_params:
                example_val = self._get_example_value(param).strip('"')
                if param.schema_type == 'string':
                    lines.append(f"        {param.name} = '{example_val}'")
                else:
                    lines.append(f"        {param.name} = {example_val}")
            lines.append("")
        
        # URL oluşturma
        if path_params:
            lines.append("        # Path parametrelerini URL'ye yerleştir")
            url_template = self._create_url_template(endpoint.path)
            lines.append(f'        url = f"{{self.base_url}}{url_template}"')
        else:
            lines.append(f'        url = f"{{self.base_url}}{endpoint.path}"')
        
        lines.append("")
        
        # Query parametreleri
        if query_params:
            lines.append("        # Query parametreleri")
            lines.append("        params = {")
            for param in query_params:
                lines.append(f'            "{param.name}": {param.name},')
            lines.append("        }")
            lines.append("")
        
        # Headers
        if header_params:
            lines.append("        # Headers")
            lines.append("        headers = {")
            for param in header_params:
                example_val = self._get_example_value(param)
                lines.append(f'            "{param.name}": {example_val},')
            lines.append("        }")
            lines.append("")
        
        # Request body
        if endpoint.request_body:
            lines.append("        # Request body")
            if endpoint.request_body.example:
                body_str = json.dumps(endpoint.request_body.example, indent=12)
                lines.append(f"        payload = {body_str}")
            elif endpoint.request_body.schema_data:
                body_str = self._generate_example_from_schema(endpoint.request_body.schema_data)
                lines.append(f"        payload = {body_str}")
            else:
                lines.append('        payload = {"example": "data"}')
            lines.append("")
        
        # HTTP isteği
        method = endpoint.method.value.upper()
        if method == "GET":
            if query_params and header_params:
                lines.append("        response = requests.get(url, params=params, headers=headers)")
            elif query_params:
                lines.append("        response = requests.get(url, params=params)")
            elif header_params:
                lines.append("        response = requests.get(url, headers=headers)")
            else:
                lines.append("        response = requests.get(url)")
        elif method == "POST":
            if query_params and header_params and endpoint.request_body:
                lines.append("        response = requests.post(url, params=params, headers=headers, json=payload)")
            elif query_params and header_params:
                lines.append("        response = requests.post(url, params=params, headers=headers)")
            elif query_params and endpoint.request_body:
                lines.append("        response = requests.post(url, params=params, json=payload)")
            elif header_params and endpoint.request_body:
                lines.append("        response = requests.post(url, headers=headers, json=payload)")
            elif query_params:
                lines.append("        response = requests.post(url, params=params)")
            elif header_params:
                lines.append("        response = requests.post(url, headers=headers)")
            elif endpoint.request_body:
                lines.append("        response = requests.post(url, json=payload)")
            else:
                lines.append("        response = requests.post(url)")
        elif method == "PUT":
            if query_params and header_params and endpoint.request_body:
                lines.append("        response = requests.put(url, params=params, headers=headers, json=payload)")
            elif query_params and header_params:
                lines.append("        response = requests.put(url, params=params, headers=headers)")
            elif query_params and endpoint.request_body:
                lines.append("        response = requests.put(url, params=params, json=payload)")
            elif header_params and endpoint.request_body:
                lines.append("        response = requests.put(url, headers=headers, json=payload)")
            elif query_params:
                lines.append("        response = requests.put(url, params=params)")
            elif header_params:
                lines.append("        response = requests.put(url, headers=headers)")
            elif endpoint.request_body:
                lines.append("        response = requests.put(url, json=payload)")
            else:
                lines.append("        response = requests.put(url)")
        elif method == "DELETE":
            if query_params and header_params:
                lines.append("        response = requests.delete(url, params=params, headers=headers)")
            elif query_params:
                lines.append("        response = requests.delete(url, params=params)")
            elif header_params:
                lines.append("        response = requests.delete(url, headers=headers)")
            else:
                lines.append("        response = requests.delete(url)")
        
        lines.append("")
        
        # Doğrulamalar
        expected_codes = self._get_expected_status_codes(endpoint)
        lines.append(f"        # Temel doğrulamalar")
        lines.append(f"        assert response.status_code in {expected_codes}")
        lines.append("")
        
        # JSON response kontrolü
        if self._should_have_json_response(endpoint):
            lines.append("        # JSON response kontrolü")
            lines.append("        assert response.headers.get('content-type', '').startswith('application/json')")
            lines.append("        json_data = response.json()")
            lines.append("        assert isinstance(json_data, (dict, list))")
            lines.append("")
        
        # Response süresi kontrolü
        lines.append("        # Response süresi kontrolü")
        lines.append("        assert response.elapsed.total_seconds() < 30")
        lines.append("")
        
        # Başarı mesajı
        lines.append(f'        print(f"✓ {endpoint.method.value.upper()} {endpoint.path} - Basic test - Status: {{response.status_code}}")')
        
        return lines
    
    def _create_parameter_variation_tests(self, endpoint: Endpoint, base_url: str) -> List[List[str]]:
        """Parametre varyasyonları için ek testler oluştur"""
        tests = []
        
        # Gerekli parametre eksikse hata testi
        required_params = [p for p in endpoint.parameters if p.required]
        if required_params:
            missing_param_test = self._create_missing_param_test(endpoint, required_params[0], base_url)
            tests.append(missing_param_test)
        
        return tests
    
    def _create_missing_param_test(self, endpoint: Endpoint, missing_param: Parameter, base_url: str) -> List[str]:
        """Eksik parametre testi oluştur"""
        lines = []
        
        lines.append(f"    def test_{endpoint.method.value}_{self._generate_method_suffix(endpoint.path)}_missing_{missing_param.name}(self):")
        lines.append(f'        """{endpoint.method.value.upper()} {endpoint.path} - Missing required parameter {missing_param.name}"""')
        lines.append("")
        
        if missing_param.type == ParameterType.PATH:
            # Path parametresi eksikse, URL'de {param} yerine geçersiz bir değer kullan
            lines.append("        # Eksik path parametresi ile test")
            if missing_param.schema_type == 'string':
                invalid_value = '"invalid"'
            else:
                invalid_value = '999999'
            
            # URL'de parametreyi geçersiz değerle değiştir
            url_with_invalid = endpoint.path.replace(f"{{{missing_param.name}}}", str(invalid_value).strip('"'))
            lines.append(f"        {missing_param.name} = {invalid_value}")
            lines.append(f'        url = f"{{self.base_url}}{url_with_invalid}"')
        else:
            # Normal URL ama parametre gönderme
            lines.append(f'        url = f"{{self.base_url}}{endpoint.path}"')
        
        lines.append("")
        
        # HTTP isteği (parametresiz veya geçersiz parametre ile)
        method = endpoint.method.value.upper()
        if method == "GET":
            lines.append("        response = requests.get(url)")
        elif method == "POST":
            lines.append("        response = requests.post(url)")
        elif method == "PUT":
            lines.append("        response = requests.put(url)")
        elif method == "DELETE":
            lines.append("        response = requests.delete(url)")
        
        lines.append("")
        
        # Hata durumu doğrulaması - 400, 422 veya 404 olabilir
        lines.append("        # Hata durumu doğrulaması (400, 422 veya 404)")
        lines.append("        assert response.status_code in [400, 422, 404]")
        lines.append("")
        
        # Response süresi kontrolü
        lines.append("        # Response süresi kontrolü")
        lines.append("        assert response.elapsed.total_seconds() < 30")
        lines.append("")
        
        # Başarı mesajı
        lines.append(f'        print(f"✓ {endpoint.method.value.upper()} {endpoint.path} - Missing/Invalid parameter {missing_param.name} - Status: {{response.status_code}}")')
        
        return lines
    
    def _generate_class_name(self, endpoint: Endpoint) -> str:
        """Endpoint'ten sınıf adı üret"""
        path_parts = [part for part in endpoint.path.split('/') if part and not part.startswith('{')]
        method_name = endpoint.method.value.capitalize()
        
        if path_parts:
            class_name = ''.join(word.capitalize() for word in path_parts) + method_name
        else:
            class_name = f"Root{method_name}"
        
        # Operation ID varsa onu kullan
        if endpoint.operation_id:
            class_name = endpoint.operation_id.replace('_', ' ').title().replace(' ', '')
        
        return class_name
    
    def _generate_file_name(self, path: str) -> str:
        """Path'ten dosya adı üret"""
        path_parts = [part for part in path.split('/') if part and not part.startswith('{')]
        return '_'.join(path_parts) if path_parts else 'root'
    
    def _create_url_template(self, path: str) -> str:
        """URL template'i oluştur"""
        import re
        # Path parametrelerini bul ve değiştir
        return re.sub(r'\{([^}]+)\}', r'{\1}', path)
    
    def _generate_params_signature(self, query_params: List[Parameter], path_params: List[Parameter]) -> str:
        """Test metodu parametre imzasını oluştur"""
        params = []
        
        for param in path_params + query_params:
            if param.required:
                params.append(f"{param.name}: {self._get_python_type(param)}")
            else:
                default_value = self._get_example_value(param) or "None"
                params.append(f"{param.name}: {self._get_python_type(param)} = {default_value}")
        
        return ", ".join(params)
    
    def _get_python_type(self, param: Parameter) -> str:
        """Pydantic tipini Python tipine çevir"""
        type_map = {
            'string': 'str',
            'integer': 'int',
            'number': 'float',
            'boolean': 'bool',
            'array': 'list',
            'object': 'dict'
        }
        return type_map.get(param.schema_type, 'Any')
    
    def _get_example_value(self, param: Parameter) -> Any:
        """Parametre için örnek değer üret"""
        if param.example is not None:
            return repr(param.example)
        
        # Tip bazlı örnek değerler
        if param.schema_type == 'string':
            return f'"test_{param.name}"'
        elif param.schema_type == 'integer':
            return '1'
        elif param.schema_type == 'number':
            return '1.0'
        elif param.schema_type == 'boolean':
            return 'True'
        else:
            return '"example"'
    
    def _generate_example_from_schema(self, schema: Dict[str, Any]) -> str:
        """Schema'dan örnek data oluştur"""
        try:
            example_data = {}
            
            if 'properties' in schema:
                for prop_name, prop_schema in schema['properties'].items():
                    prop_type = prop_schema.get('type', 'string')
                    if prop_type == 'string':
                        example_data[prop_name] = f"test_{prop_name}"
                    elif prop_type == 'integer':
                        example_data[prop_name] = 1
                    elif prop_type == 'boolean':
                        example_data[prop_name] = True
                    else:
                        example_data[prop_name] = "example"
            
            return json.dumps(example_data, indent=12)
        except:
            return '{"example": "data"}'
    
    def _get_expected_status_codes(self, endpoint: Endpoint) -> List[int]:
        """Beklenen status kodlarını belirle"""
        codes = []
        
        for response in endpoint.responses:
            if 200 <= response.status_code < 300:
                codes.append(response.status_code)
        
        # Hiç başarılı kod yoksa varsayılanlar
        if not codes:
            if endpoint.method == HTTPMethod.POST:
                codes = [201, 200]
            elif endpoint.method == HTTPMethod.DELETE:
                codes = [204, 200]
            else:
                codes = [200]
        
        return codes
    
    def _should_have_json_response(self, endpoint: Endpoint) -> bool:
        """JSON response beklenip beklenmediğini kontrol et"""
        for response in endpoint.responses:
            if response.status_code == 200 and response.content_type == "application/json":
                return True
        return False
    
    def _generate_method_suffix(self, path: str) -> str:
        """Metod adı soneki oluştur"""
        path_parts = [part for part in path.split('/') if part and not part.startswith('{')]
        return '_'.join(path_parts[:3]) if path_parts else 'root'