from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field
from enum import Enum


class HTTPMethod(str, Enum):
    GET = "get"
    POST = "post"
    PUT = "put"
    DELETE = "delete"
    PATCH = "patch"
    HEAD = "head"
    OPTIONS = "options"


class ParameterType(str, Enum):
    QUERY = "query"
    PATH = "path"
    HEADER = "header"
    COOKIE = "cookie"
    BODY = "body"


class Parameter(BaseModel):
    name: str
    type: ParameterType
    required: bool = False
    description: Optional[str] = None
    schema_type: Optional[str] = None
    example: Optional[Any] = None
    default: Optional[Any] = None


class RequestBody(BaseModel):
    description: Optional[str] = None
    required: bool = False
    content_type: str = "application/json"
    schema_data: Optional[Dict[str, Any]] = Field(default=None, alias="schema")
    example: Optional[Any] = None


class Response(BaseModel):
    status_code: int
    description: Optional[str] = None
    content_type: str = "application/json"
    schema_data: Optional[Dict[str, Any]] = Field(default=None, alias="schema")
    example: Optional[Any] = None


class Endpoint(BaseModel):
    path: str
    method: HTTPMethod
    operation_id: Optional[str] = None
    summary: Optional[str] = None
    description: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    parameters: List[Parameter] = Field(default_factory=list)
    request_body: Optional[RequestBody] = None
    responses: List[Response] = Field(default_factory=list)
    security: Optional[List[Dict[str, List[str]]]] = None


class APISpecInfo(BaseModel):
    title: str
    version: str
    description: Optional[str] = None
    contact: Optional[Dict[str, str]] = None
    license: Optional[Dict[str, str]] = None


class OpenAPIParser:
    """OpenAPI/Swagger belirtimi ayrıştırıcı"""
    
    def __init__(self, spec: Dict[str, Any]):
        self.spec = spec
        self.openapi_version = spec.get("openapi", spec.get("swagger", "2.0"))
        self.info = self._parse_info()
        self.endpoints = self._parse_endpoints()
    
    def _parse_info(self) -> APISpecInfo:
        """API bilgilerini ayrıştır"""
        info_data = self.spec.get("info", {})
        return APISpecInfo(
            title=info_data.get("title", "API"),
            version=info_data.get("version", "1.0.0"),
            description=info_data.get("description"),
            contact=info_data.get("contact"),
            license=info_data.get("license")
        )
    
    def _parse_endpoints(self) -> List[Endpoint]:
        """Tüm uç noktaları ayrıştır"""
        endpoints = []
        paths = self.spec.get("paths", {})
        
        for path, path_item in paths.items():
            for method, operation in path_item.items():
                if method.upper() in [m.value.upper() for m in HTTPMethod]:
                    endpoint = self._parse_endpoint(
                        path=path,
                        method=HTTPMethod(method.lower()),
                        operation=operation,
                        path_item=path_item
                    )
                    endpoints.append(endpoint)
        
        return endpoints
    
    def _parse_endpoint(self, path: str, method: HTTPMethod, operation: Dict[str, Any], path_item: Dict[str, Any]) -> Endpoint:
        """Tek bir uç noktayı ayrıştır"""
        # Ortak parametreleri al (path seviyesi)
        common_params = self._parse_parameters(path_item.get("parameters", []))
        
        # Operasyon seviyesi parametreleri al
        operation_params = self._parse_parameters(operation.get("parameters", []))
        
        # Tüm parametreleri birleştir
        all_params = common_params + operation_params
        
        # Request body ayrıştır
        request_body = None
        if method in [HTTPMethod.POST, HTTPMethod.PUT, HTTPMethod.PATCH]:
            request_body = self._parse_request_body(operation.get("requestBody", {}))
        
        # Response'ları ayrıştır
        responses = self._parse_responses(operation.get("responses", {}))
        
        return Endpoint(
            path=path,
            method=method,
            operation_id=operation.get("operationId"),
            summary=operation.get("summary"),
            description=operation.get("description"),
            tags=operation.get("tags", []),
            parameters=all_params,
            request_body=request_body,
            responses=responses,
            security=operation.get("security")
        )
    
    def _parse_parameters(self, params: List[Dict[str, Any]]) -> List[Parameter]:
        """Parametre listesini ayrıştır"""
        parameters = []
        
        for param in params:
            param_type = ParameterType(param.get("in", "query"))
            schema = param.get("schema", {})
            
            parameter = Parameter(
                name=param.get("name", ""),
                type=param_type,
                required=param.get("required", False),
                description=param.get("description"),
                schema_type=schema.get("type"),
                example=param.get("example") or schema.get("example"),
                default=param.get("default") or schema.get("default")
            )
            parameters.append(parameter)
        
        return parameters
    
    def _parse_request_body(self, request_body: Dict[str, Any]) -> Optional[RequestBody]:
        """Request body ayrıştır"""
        if not request_body:
            return None
        
        content = request_body.get("content", {})
        json_content = content.get("application/json", {})
        
        return RequestBody(
            description=request_body.get("description"),
            required=request_body.get("required", False),
            content_type="application/json",
            schema=json_content.get("schema"),
            example=json_content.get("example")
        )
    
    def _parse_responses(self, responses: Dict[str, Any]) -> List[Response]:
        """Response'ları ayrıştır"""
        parsed_responses = []
        
        for status_code, response_data in responses.items():
            try:
                status_int = int(status_code)
            except ValueError:
                continue
            
            content = response_data.get("content", {})
            json_content = content.get("application/json", {})
            
            response = Response(
                status_code=status_int,
                description=response_data.get("description"),
                content_type="application/json",
                schema=json_content.get("schema"),
                example=json_content.get("example")
            )
            parsed_responses.append(response)
        
        return parsed_responses
    
    def get_endpoints_by_tag(self, tag: str) -> List[Endpoint]:
        """Belirli bir etikete sahip uç noktaları getir"""
        return [ep for ep in self.endpoints if tag in ep.tags]
    
    def get_endpoints_by_method(self, method: HTTPMethod) -> List[Endpoint]:
        """Belirli bir HTTP metoduna sahip uç noktaları getir"""
        return [ep for ep in self.endpoints if ep.method == method]
    
    def get_endpoint_by_operation_id(self, operation_id: str) -> Optional[Endpoint]:
        """Operation ID'ye göre uç nokta bul"""
        for ep in self.endpoints:
            if ep.operation_id == operation_id:
                return ep
        return None
    
    def get_all_tags(self) -> List[str]:
        """Tüm etiketleri getir"""
        tags = set()
        for ep in self.endpoints:
            tags.update(ep.tags)
        return sorted(list(tags))
    
    def get_paths(self) -> List[str]:
        """Tüm path'leri getir"""
        return sorted(list(set(ep.path for ep in self.endpoints)))