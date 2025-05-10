#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
BeOnSafe - API Gateway
Interface para integração com sistemas externos e gerenciamento de APIs
"""

import os
import json
import requests
import logging
import hmac
import hashlib
import time
import base64
from datetime import datetime
from urllib.parse import urljoin
from dotenv import load_dotenv

# Configuração de logs
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("logs/api.log")
    ]
)

logger = logging.getLogger("api_gateway")

# Carrega variáveis de ambiente
load_dotenv()

class APIGateway:
    """Gateway para interfaces de API da BeOnSafe"""
    
    def __init__(self):
        self.api_base_url = os.getenv("API_BASE_URL", "https://api.beonsafe.com.br")
        self.api_version = os.getenv("API_VERSION", "v1")
        self.api_key = os.getenv("API_KEY")
        self.secret_key = os.getenv("API_SECRET")
        self.session = requests.Session()
        
        # Configuração da sessão
        self.session.headers.update({
            "User-Agent": "BeOnSafe Agent/1.0",
            "Content-Type": "application/json",
            "Accept": "application/json"
        })
        
        logger.info(f"API Gateway inicializado: {self.api_base_url}/{self.api_version}")
    
    def _get_full_url(self, endpoint):
        """Constrói a URL completa para o endpoint"""
        return urljoin(f"{self.api_base_url}/{self.api_version}/", endpoint.lstrip('/'))
    
    def _generate_signature(self, data, timestamp):
        """Gera uma assinatura HMAC para autenticação"""
        if not self.secret_key:
            return None
            
        # Cria o payload para assinatura
        payload = f"{timestamp}.{json.dumps(data) if isinstance(data, dict) else data}"
        
        # Gera HMAC usando SHA-256
        signature = hmac.new(
            self.secret_key.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).digest()
        
        # Retorna em formato base64
        return base64.b64encode(signature).decode('utf-8')
    
    def _prepare_auth_headers(self, data=None):
        """Prepara cabeçalhos de autenticação"""
        headers = {}
        timestamp = str(int(time.time()))
        
        if self.api_key:
            headers["X-API-Key"] = self.api_key
            headers["X-Timestamp"] = timestamp
            
            if self.secret_key and data:
                headers["X-Signature"] = self._generate_signature(data, timestamp)
                
        return headers
    
    def get(self, endpoint, params=None):
        """Executa uma requisição GET"""
        url = self._get_full_url(endpoint)
        headers = self._prepare_auth_headers()
        
        try:
            response = self.session.get(url, params=params, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro na requisição GET para {url}: {str(e)}")
            return {"error": str(e), "status_code": getattr(e.response, 'status_code', None)}
    
    def post(self, endpoint, data):
        """Executa uma requisição POST"""
        url = self._get_full_url(endpoint)
        headers = self._prepare_auth_headers(data)
        
        try:
            response = self.session.post(url, json=data, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro na requisição POST para {url}: {str(e)}")
            return {"error": str(e), "status_code": getattr(e.response, 'status_code', None)}
    
    def put(self, endpoint, data):
        """Executa uma requisição PUT"""
        url = self._get_full_url(endpoint)
        headers = self._prepare_auth_headers(data)
        
        try:
            response = self.session.put(url, json=data, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro na requisição PUT para {url}: {str(e)}")
            return {"error": str(e), "status_code": getattr(e.response, 'status_code', None)}
    
    def delete(self, endpoint, params=None):
        """Executa uma requisição DELETE"""
        url = self._get_full_url(endpoint)
        headers = self._prepare_auth_headers()
        
        try:
            response = self.session.delete(url, params=params, headers=headers)
            response.raise_for_status()
            return response.json() if response.content else {"status": "success"}
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro na requisição DELETE para {url}: {str(e)}")
            return {"error": str(e), "status_code": getattr(e.response, 'status_code', None)}

class RealEstateAPI:
    """API específica para o setor imobiliário"""
    
    def __init__(self):
        self.api = APIGateway()
        self.base_endpoint = "real-estate"
    
    def get_properties(self, filters=None):
        """Obtém lista de propriedades com filtros opcionais"""
        return self.api.get(f"{self.base_endpoint}/properties", params=filters)
    
    def get_property_details(self, property_id):
        """Obtém detalhes de uma propriedade específica"""
        return self.api.get(f"{self.base_endpoint}/properties/{property_id}")
    
    def create_lead(self, lead_data):
        """Registra um novo lead imobiliário"""
        return self.api.post(f"{self.base_endpoint}/leads", data=lead_data)
    
    def schedule_visit(self, property_id, visit_data):
        """Agenda uma visita a um imóvel"""
        return self.api.post(f"{self.base_endpoint}/properties/{property_id}/visits", data=visit_data)

class DealershipAPI:
    """API específica para concessionárias"""
    
    def __init__(self):
        self.api = APIGateway()
        self.base_endpoint = "dealership"
    
    def get_vehicles(self, filters=None):
        """Obtém lista de veículos com filtros opcionais"""
        return self.api.get(f"{self.base_endpoint}/vehicles", params=filters)
    
    def get_vehicle_details(self, vehicle_id):
        """Obtém detalhes de um veículo específico"""
        return self.api.get(f"{self.base_endpoint}/vehicles/{vehicle_id}")
    
    def create_lead(self, lead_data):
        """Registra um novo lead interessado em veículos"""
        return self.api.post(f"{self.base_endpoint}/leads", data=lead_data)
    
    def schedule_test_drive(self, vehicle_id, test_drive_data):
        """Agenda um test drive"""
        return self.api.post(f"{self.base_endpoint}/vehicles/{vehicle_id}/test-drive", data=test_drive_data)
    
    def get_financing_options(self, vehicle_id, customer_data=None):
        """Obtém opções de financiamento para um veículo"""
        return self.api.post(f"{self.base_endpoint}/vehicles/{vehicle_id}/financing", data=customer_data or {})

# Função de demonstração
def demo():
    """Demonstração simples de uso das APIs"""
    # Exemplo de uso da API imobiliária
    real_estate_api = RealEstateAPI()
    properties = real_estate_api.get_properties({"price_max": 500000, "bedrooms": 2})
    print("\n=== Imóveis Disponíveis ===")
    print(json.dumps(properties, indent=2))
    
    # Exemplo de uso da API de concessionária
    dealership_api = DealershipAPI()
    vehicles = dealership_api.get_vehicles({"type": "SUV", "price_max": 150000})
    print("\n=== Veículos Disponíveis ===")
    print(json.dumps(vehicles, indent=2))
    
    # Exemplo de agendamento de test drive
    test_drive = dealership_api.schedule_test_drive(
        "vehicle123", 
        {
            "customer_name": "João Silva",
            "customer_email": "joao@example.com",
            "customer_phone": "11999998888",
            "datetime": "2023-12-15T14:30:00",
            "notes": "Cliente interessado em financiamento"
        }
    )
    print("\n=== Agendamento de Test Drive ===")
    print(json.dumps(test_drive, indent=2))

if __name__ == "__main__":
    # Cria pasta de logs se não existir
    os.makedirs("logs", exist_ok=True)
    
    # Mock para teste local
    if not os.getenv("API_BASE_URL"):
        print("API_BASE_URL não configurada. Usando mock local para demonstração.")
        
        # Monkey patch para simular respostas da API
        def mock_get(self, endpoint, params=None):
            if "properties" in endpoint:
                return {"properties": [{"id": "prop123", "type": "Apartamento", "price": 450000}]}
            elif "vehicles" in endpoint:
                return {"vehicles": [{"id": "vehicle123", "model": "HRV", "price": 120000}]}
            return {"message": "Mock response", "endpoint": endpoint}
            
        def mock_post(self, endpoint, data):
            return {"success": True, "data": data, "endpoint": endpoint}
            
        APIGateway.get = mock_get
        APIGateway.post = mock_post
    
    # Executa demonstração
    demo() 