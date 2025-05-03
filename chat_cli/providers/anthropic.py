"""
Proveedor para modelos de Anthropic con soporte para Model Context Protocol (M.C.P).

Este módulo implementa la integración con la API de Anthropic y añade soporte
para el Model Context Protocol (M.C.P), permitiendo que los modelos de Anthropic
como Claude puedan acceder a recursos externos, herramientas y contexto adicional.

Autor: Cascade
Fecha: Mayo 2025
"""

import os
import json
import requests
from typing import Dict, List, Any, Generator, Optional, Union

# Constantes para la API de Anthropic
ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"
DEFAULT_MODEL = "claude-3-opus-20240229"

# Constantes para Model Context Protocol (M.C.P)
MCP_ENABLED = False  # Por defecto desactivado hasta configuración completa
MCP_VERSION = "0.1.0"  # Versión del protocolo implementada

class AnthropicProvider:
    """
    Proveedor para modelos de Anthropic con soporte para Model Context Protocol.
    
    Permite interactuar con modelos como Claude y utilizar las capacidades
    del Model Context Protocol para acceder a recursos externos y herramientas.
    """
    
    def __init__(self, api_key=None, model=DEFAULT_MODEL, mcp_enabled=MCP_ENABLED):
        """
        Inicializa el proveedor de Anthropic.
        
        Args:
            api_key: Clave de API de Anthropic. Si no se proporciona, se intenta obtener de ANTHROPIC_API_KEY.
            model: Modelo de Anthropic a utilizar (por defecto: claude-3-opus-20240229).
            mcp_enabled: Si es True, activa el soporte para Model Context Protocol.
        """
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY", "API_KEY_AQUI")
        self.model = model
        self.history = []
        self.mcp_enabled = mcp_enabled
        self.mcp_servers = []  # Lista de servidores MCP conectados
    
    def send_message(self, prompt: str) -> str:
        """
        Envía un mensaje al modelo de Anthropic y devuelve la respuesta.
        
        Args:
            prompt: Texto del mensaje a enviar.
            
        Returns:
            Respuesta del modelo como texto.
        """
        try:
            # Preparar mensajes con historial
            messages = self._prepare_messages(prompt)
            
            # Configurar parámetros de la solicitud
            data = {
                "model": self.model,
                "messages": messages,
                "max_tokens": 1024
            }
            
            # Añadir configuración MCP si está habilitado
            if self.mcp_enabled:
                data["mcp_config"] = self._get_mcp_config()
            
            # Realizar la solicitud a la API
            headers = {
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            }
            
            response = requests.post(
                ANTHROPIC_API_URL,
                headers=headers,
                json=data
            )
            
            # Verificar respuesta
            response.raise_for_status()
            result = response.json()
            
            # Extraer contenido de la respuesta
            content = result.get("content", [{}])[0].get("text", "")
            
            # Guardar en historial
            self.history.append({"role": "assistant", "content": content})
            
            return content
            
        except Exception as e:
            return f"[Anthropic] Error: {e}"
    
    def stream_message(self, prompt: str) -> Generator[str, None, None]:
        """
        Envía un mensaje al modelo de Anthropic y devuelve la respuesta en streaming.
        
        Args:
            prompt: Texto del mensaje a enviar.
            
        Yields:
            Fragmentos de texto de la respuesta del modelo.
        """
        try:
            # Preparar mensajes con historial
            messages = self._prepare_messages(prompt)
            
            # Configurar parámetros de la solicitud
            data = {
                "model": self.model,
                "messages": messages,
                "max_tokens": 1024,
                "stream": True
            }
            
            # Añadir configuración MCP si está habilitado
            if self.mcp_enabled:
                data["mcp_config"] = self._get_mcp_config()
            
            # Realizar la solicitud a la API
            headers = {
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            }
            
            response = requests.post(
                ANTHROPIC_API_URL,
                headers=headers,
                json=data,
                stream=True
            )
            
            # Verificar respuesta
            response.raise_for_status()
            
            # Procesar respuesta en streaming
            full_response = ""
            for line in response.iter_lines():
                if not line:
                    continue
                    
                # Eliminar el prefijo "data: " y decodificar
                if line.startswith(b"data: "):
                    line = line[6:]
                    
                # Ignorar el mensaje [DONE]
                if line == b"[DONE]":
                    break
                    
                try:
                    data = json.loads(line)
                    if "content" in data and data["content"]:
                        delta = data["content"][0].get("text", "")
                        if delta:
                            full_response += delta
                            yield delta
                except Exception as e:
                    yield f"[Error parsing stream: {e}]"
            
            # Guardar respuesta completa en historial
            if full_response:
                self.history.append({"role": "assistant", "content": full_response})
                
        except Exception as e:
            yield f"[Anthropic] Error en streaming: {e}"
    
    def _prepare_messages(self, prompt: str) -> List[Dict[str, str]]:
        """
        Prepara los mensajes para enviar a la API, incluyendo el historial.
        
        Args:
            prompt: Texto del mensaje a enviar.
            
        Returns:
            Lista de mensajes en formato compatible con la API de Anthropic.
        """
        # Añadir mensaje del usuario al historial
        self.history.append({"role": "user", "content": prompt})
        
        # Convertir historial al formato esperado por la API
        messages = []
        for msg in self.history:
            role = msg["role"]
            # Anthropic usa "assistant" y "user" como roles
            if role not in ["assistant", "user"]:
                role = "user"  # Por defecto, tratar como usuario
            
            messages.append({
                "role": role,
                "content": msg["content"]
            })
        
        return messages
    
    def _get_mcp_config(self) -> Dict[str, Any]:
        """
        Obtiene la configuración para Model Context Protocol.
        
        Returns:
            Diccionario con la configuración MCP.
        """
        # Configuración básica de MCP
        config = {
            "version": MCP_VERSION,
            "enabled": self.mcp_enabled,
            "servers": self.mcp_servers,
            "capabilities": {
                "tools": True,
                "resources": True,
                "prompts": True
            }
        }
        
        return config
    
    def set_mcp_enabled(self, enabled: bool) -> None:
        """
        Activa o desactiva el soporte para Model Context Protocol.
        
        Args:
            enabled: True para activar, False para desactivar.
        """
        self.mcp_enabled = enabled
    
    def add_mcp_server(self, server_url: str, capabilities: Optional[Dict[str, bool]] = None) -> None:
        """
        Añade un servidor MCP a la lista de servidores disponibles.
        
        Args:
            server_url: URL del servidor MCP.
            capabilities: Diccionario con las capacidades del servidor.
        """
        if capabilities is None:
            capabilities = {
                "tools": True,
                "resources": True,
                "prompts": True
            }
        
        self.mcp_servers.append({
            "url": server_url,
            "capabilities": capabilities
        })
    
    def clear_mcp_servers(self) -> None:
        """Elimina todos los servidores MCP registrados."""
        self.mcp_servers = []
