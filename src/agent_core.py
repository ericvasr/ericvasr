#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
BeOnSafe - Núcleo de Agentes de IA
Implementação central dos agentes SDR para imobiliárias e concessionárias
"""

import os
import json
import logging
from datetime import datetime
from dotenv import load_dotenv

# Configuração de logs
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("logs/agent.log")
    ]
)

logger = logging.getLogger("agent_core")

# Carrega variáveis de ambiente
load_dotenv()

class Agent:
    """Classe base para todos os agentes de IA da BeOnSafe"""
    
    def __init__(self, name, agent_type="generic"):
        self.name = name
        self.agent_type = agent_type
        self.created_at = datetime.now()
        self.conversation_history = []
        self.settings = {}
        self.auth_token = os.getenv("API_KEY")
        logger.info(f"Agente {self.name} ({self.agent_type}) inicializado")
    
    def load_settings(self, settings_file=None):
        """Carrega configurações do agente"""
        if settings_file and os.path.exists(settings_file):
            with open(settings_file, 'r', encoding='utf-8') as f:
                self.settings = json.load(f)
                logger.info(f"Configurações carregadas de {settings_file}")
        else:
            # Configurações padrão
            self.settings = {
                "response_time": 2.0,
                "max_retries": 3,
                "confidence_threshold": 0.7,
                "language": "pt-br",
                "use_knowledge_base": True
            }
            logger.info("Usando configurações padrão")
        
        return self.settings
    
    def process_message(self, message, context=None):
        """Processa uma mensagem recebida"""
        if not message:
            return {"error": "Mensagem vazia"}
            
        # Adiciona à história da conversa
        self.conversation_history.append({
            "role": "user",
            "content": message,
            "timestamp": datetime.now().isoformat()
        })
        
        # Lógica de processamento (a ser implementada por subclasses)
        response = self._generate_response(message, context)
        
        # Adiciona resposta à história da conversa
        self.conversation_history.append({
            "role": "agent",
            "content": response,
            "timestamp": datetime.now().isoformat()
        })
        
        return response
    
    def _generate_response(self, message, context):
        """Método interno para gerar resposta (deve ser sobrescrito)"""
        return "Esta é uma resposta genérica. Implemente esta função nas subclasses."
    
    def get_conversation_history(self):
        """Retorna o histórico de conversas"""
        return self.conversation_history
    
    def save_state(self, filename=None):
        """Salva o estado atual do agente"""
        if not filename:
            filename = f"data/agents/{self.name}_{self.agent_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        state = {
            "name": self.name,
            "agent_type": self.agent_type,
            "created_at": self.created_at.isoformat(),
            "settings": self.settings,
            "conversation_history": self.conversation_history
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
            
        logger.info(f"Estado do agente salvo em {filename}")
        return filename

class RealEstateAgent(Agent):
    """Agente especializado para o setor imobiliário"""
    
    def __init__(self, name):
        super().__init__(name, agent_type="real_estate")
        self.property_database = []
        self.client_preferences = {}
        
    def load_properties(self, properties_file):
        """Carrega base de imóveis"""
        if os.path.exists(properties_file):
            with open(properties_file, 'r', encoding='utf-8') as f:
                self.property_database = json.load(f)
                logger.info(f"Carregadas {len(self.property_database)} propriedades")
        return self.property_database
    
    def _generate_response(self, message, context):
        """Gera resposta específica para contexto imobiliário"""
        # Implementação simplificada
        if "preço" in message.lower() or "valor" in message.lower():
            return "Temos imóveis em diversas faixas de preço. Qual é o seu orçamento?"
        elif "visita" in message.lower() or "visitar" in message.lower():
            return "Ótimo! Posso agendar uma visita para você. Qual seria o melhor dia e horário?"
        elif "localização" in message.lower() or "bairro" in message.lower():
            return "Temos opções em vários bairros da cidade. Alguma região específica de interesse?"
        else:
            return "Como agente imobiliário, posso ajudar a encontrar o imóvel ideal para você. Conte-me mais sobre o que está procurando."

class CarDealershipAgent(Agent):
    """Agente especializado para concessionárias"""
    
    def __init__(self, name):
        super().__init__(name, agent_type="car_dealership")
        self.vehicle_inventory = []
        self.financing_options = {}
        
    def load_inventory(self, inventory_file):
        """Carrega base de veículos"""
        if os.path.exists(inventory_file):
            with open(inventory_file, 'r', encoding='utf-8') as f:
                self.vehicle_inventory = json.load(f)
                logger.info(f"Carregados {len(self.vehicle_inventory)} veículos")
        return self.vehicle_inventory
    
    def _generate_response(self, message, context):
        """Gera resposta específica para contexto de concessionária"""
        # Implementação simplificada
        if "test drive" in message.lower():
            return "Claro! Podemos agendar um test drive. Qual modelo você gostaria de experimentar?"
        elif "financiamento" in message.lower():
            return "Temos excelentes opções de financiamento com taxas a partir de 0,99% ao mês. Gostaria de uma simulação?"
        elif "promoção" in message.lower() or "desconto" in message.lower():
            return "Temos promoções especiais este mês! Aproveite até 20% de desconto em modelos selecionados."
        else:
            return "Como especialista em vendas de veículos, posso ajudar a encontrar o carro ideal para você. Qual tipo de veículo você procura?"

# Função de demonstração
def demo():
    """Demonstração simples de uso dos agentes"""
    # Agente imobiliário
    real_estate_agent = RealEstateAgent("Amanda")
    response1 = real_estate_agent.process_message("Olá, estou procurando um apartamento na zona sul.")
    print(f"\nAgente Imobiliário: {response1}")
    
    response2 = real_estate_agent.process_message("Qual o preço médio dos imóveis nessa região?")
    print(f"Agente Imobiliário: {response2}")
    
    # Agente de concessionária
    car_agent = CarDealershipAgent("Carlos")
    response3 = car_agent.process_message("Bom dia, estou interessado em um SUV.")
    print(f"\nAgente Concessionária: {response3}")
    
    response4 = car_agent.process_message("Vocês oferecem financiamento?")
    print(f"Agente Concessionária: {response4}")
    
    print("\nHistórico do Agente Imobiliário:")
    for msg in real_estate_agent.get_conversation_history():
        print(f"[{msg['role']}]: {msg['content']}")

if __name__ == "__main__":
    # Cria pasta de logs se não existir
    os.makedirs("logs", exist_ok=True)
    
    # Executa demonstração
    demo() 