from textual.app import App, ComposeResult
from textual.containers import Container, ScrollableContainer
from textual.widgets import Header, Footer, Input, Static
from textual.binding import Binding
from rich.panel import Panel
from rich.align import Align
import asyncio
import os
from datetime import datetime
from .history import load_history, save_history, clear_history, export_history_txt

# Archivo de historial por defecto
HIST_FILE = "history.json"
EXPORT_FILE = "historial.txt"

# Constantes para Model Context Protocol
MCP_ENABLED = False  # Activar cuando se implemente completamente

class ChatApp(App):
    """Textual-based TUI para Chat CLI con historial, atajos y mejoras visuales."""
    
    TITLE = "Chat LLM TUI"
    BINDINGS = [
        Binding("ctrl+l", "limpiar_historial", "Limpiar historial"),
        Binding("ctrl+e", "exportar_historial", "Exportar historial"),
        Binding("ctrl+c", "limpiar_pantalla", "Limpiar pantalla"),
        Binding("ctrl+h", "mostrar_ayuda", "Mostrar ayuda"),
        Binding("ctrl+q", "salir", "Salir")
    ]

    def __init__(self, provider, model, stream=False):
        """Inicializa la aplicación TUI con el proveedor y modelo seleccionados."""
        super().__init__()
        self.provider = provider
        self.model = model
        self.stream = stream
        self.history = []
        self.token_count = 0
        self.last_activity = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.mcp_enabled = MCP_ENABLED
        self.status_widget = Static(f"Modelo: {model} | Tokens: 0 | Streaming: {'Activado' if stream else 'Desactivado'} | MCP: {'Desactivado'}")

    def load_and_show_history(self):
        """Carga el historial desde archivo y lo muestra en la TUI al iniciar."""
        if os.path.exists(HIST_FILE):
            try:
                self.history = load_history(HIST_FILE)
            except Exception:
                self.history = []
        else:
            self.history = []
            
        panel = self.query_one("#messages_panel", ScrollableContainer)
        
        # Eliminar todos los widgets hijos (en lugar de clear())
        widgets_to_remove = list(panel.children)
        for widget in widgets_to_remove:
            widget.remove()
            
        # Mostrar mensajes del historial
        for msg in self.history:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            align = "left" if role == "user" else "right"
            color = "green" if role == "user" else "blue"
            user_label = "Tú" if role == "user" else "LLM"
            panel.mount(Static(Align(Panel(content, title=user_label, border_style=color), align=align)))
            
        panel.scroll_end(animate=False)

    def compose(self) -> ComposeResult:
        """Define la estructura de la interfaz de usuario."""
        yield Header()
        yield ScrollableContainer(id="messages_panel")
        yield Input(placeholder="Escribe un mensaje... (Ctrl+H para ayuda)", id="input_panel")
        yield Footer()
        yield self.status_widget

    async def on_mount(self) -> None:
        """Se ejecuta al montar la aplicación."""
        self.set_focus(self.query_one("#input_panel", Input))
        self.load_and_show_history()

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """Gestiona el envío de mensajes y la respuesta del modelo."""
        text = event.value.strip()
        if not text:
            return
            
        # Comandos especiales con /
        if text.startswith("/"):
            await self._process_command(text)
            event.input.value = ""
            return
            
        panel = self.query_one("#messages_panel", ScrollableContainer)
        
        # Montar mensaje de usuario a la izquierda
        timestamp = datetime.now().strftime("%H:%M:%S")
        user_widget = Static(Align(Panel(
            text, 
            title=f"Tú [{timestamp}]", 
            border_style="green"
        ), align="left"))
        await panel.mount(user_widget)
        panel.scroll_end(animate=False)
        event.input.value = ""
        
        # Actualizar última actividad
        self.last_activity = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Guardar mensaje en historial
        self.history.append({"role": "user", "content": text, "timestamp": self.last_activity})
        save_history(self.history, HIST_FILE)
        
        # Actualizar barra de estado
        self._update_status_bar()
        
        # Montar respuesta del modelo en streaming o no
        try:
            # Mostrar indicador de "pensando..."
            thinking_widget = Static(Align(Panel(
                "Pensando...", 
                title="Estado", 
                border_style="yellow"
            ), align="center"))
            await panel.mount(thinking_widget)
            panel.scroll_end(animate=False)
            
            if self.stream and hasattr(self.provider, "stream_message"):
                # Eliminar indicador de pensando
                thinking_widget.remove()
                
                # Crear widget para respuesta en streaming
                timestamp = datetime.now().strftime("%H:%M:%S")
                resp_widget = Static(Align(Panel(
                    "", 
                    title=f"LLM [{timestamp}]", 
                    border_style="blue"
                ), align="right"))
                await panel.mount(resp_widget)
                
                # Procesar tokens en streaming
                full_response = ""
                for token in self.provider.stream_message(text):
                    self.token_count += 1
                    full_response += token
                    resp_widget.update(Align(Panel(
                        full_response, 
                        title=f"LLM [{timestamp}]", 
                        border_style="blue"
                    ), align="right"))
                    panel.scroll_end(animate=False)
                    self._update_status_bar()
                    await asyncio.sleep(0)
                
                # Guardar respuesta en historial
                self.history.append({
                    "role": "assistant", 
                    "content": full_response, 
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
                save_history(self.history, HIST_FILE)
                panel.scroll_end(animate=False)
            else:
                # Obtener respuesta completa
                response = self.provider.send_message(text)
                
                # Eliminar indicador de pensando
                thinking_widget.remove()
                
                # Mostrar respuesta
                timestamp = datetime.now().strftime("%H:%M:%S")
                model_widget = Static(Align(Panel(
                    response, 
                    title=f"LLM [{timestamp}]", 
                    border_style="blue"
                ), align="right"))
                await panel.mount(model_widget)
                panel.scroll_end(animate=False)
                
                # Actualizar conteo de tokens y guardar en historial
                self.token_count += len(response.split())
                self._update_status_bar()
                self.history.append({
                    "role": "assistant", 
                    "content": response, 
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
                save_history(self.history, HIST_FILE)
        except Exception as e:
            # Manejar errores
            if 'thinking_widget' in locals():
                thinking_widget.remove()
            error_msg = f"[Error] {e}"
            await panel.mount(Static(Align(Panel(
                error_msg, 
                title="Error", 
                border_style="red"
            ), align="center")))
            panel.scroll_end(animate=False)

    async def _process_command(self, text):
        """Procesa comandos especiales que comienzan con /."""
        panel = self.query_one("#messages_panel", ScrollableContainer)
        command = text.lower().strip()
        
        if command == "/help" or command == "/ayuda":
            await self.action_mostrar_ayuda()
        elif command == "/clear" or command == "/limpiar":
            await self.action_limpiar_pantalla()
        elif command == "/clearhistory" or command == "/limpiarhistorial":
            await self.action_limpiar_historial()
        elif command == "/export" or command == "/exportar":
            await self.action_exportar_historial()
        elif command.startswith("/mcp"):
            # Comando para activar/desactivar MCP (pendiente implementación completa)
            if " on" in command or " activar" in command:
                self.mcp_enabled = True
                await panel.mount(Static(Align(Panel(
                    "Model Context Protocol activado", 
                    title="Info", 
                    border_style="yellow"
                ), align="center")))
            elif " off" in command or " desactivar" in command:
                self.mcp_enabled = False
                await panel.mount(Static(Align(Panel(
                    "Model Context Protocol desactivado", 
                    title="Info", 
                    border_style="yellow"
                ), align="center")))
            else:
                await panel.mount(Static(Align(Panel(
                    "Uso: /mcp on|off o /mcp activar|desactivar", 
                    title="Info", 
                    border_style="yellow"
                ), align="center")))
            self._update_status_bar()
        else:
            await panel.mount(Static(Align(Panel(
                f"Comando desconocido: {text}. Escribe /help para ver los comandos disponibles.", 
                title="Info", 
                border_style="yellow"
            ), align="center")))
        panel.scroll_end(animate=False)
        
    def _update_status_bar(self):
        """Actualiza la barra de estado con información actualizada."""
        status_text = f"Modelo: {self.model} | Tokens: {self.token_count} | Streaming: {'Activado' if self.stream else 'Desactivado'} | MCP: {'Activado' if self.mcp_enabled else 'Desactivado'}"
        self.status_widget.update(status_text)
    
    async def action_limpiar_historial(self):
        """Limpia el historial de la sesión y del archivo."""
        clear_history(HIST_FILE)
        self.history = []
        self.token_count = 0
        self._update_status_bar()
        
        panel = self.query_one("#messages_panel", ScrollableContainer)
        # Eliminar todos los widgets hijos (en lugar de clear())
        widgets_to_remove = list(panel.children)
        for widget in widgets_to_remove:
            widget.remove()
            
        panel.mount(Static(Align(Panel(
            "Historial limpiado correctamente.", 
            title="Info", 
            border_style="yellow"
        ), align="center")))
        panel.scroll_end(animate=False)
        
    async def action_limpiar_pantalla(self):
        """Limpia la pantalla sin borrar el historial guardado."""
        panel = self.query_one("#messages_panel", ScrollableContainer)
        
        # Eliminar todos los widgets hijos (en lugar de clear())
        widgets_to_remove = list(panel.children)
        for widget in widgets_to_remove:
            widget.remove()
            
        panel.mount(Static(Align(Panel(
            "Pantalla limpiada. El historial sigue guardado.", 
            title="Info", 
            border_style="yellow"
        ), align="center")))
        panel.scroll_end(animate=False)
        
    async def action_exportar_historial(self):
        """Exporta el historial a un archivo de texto plano."""
        try:
            export_history_txt(self.history, EXPORT_FILE)
            panel = self.query_one("#messages_panel", ScrollableContainer)
            panel.mount(Static(Align(Panel(
                f"Historial exportado a {EXPORT_FILE}", 
                title="Info", 
                border_style="yellow"
            ), align="center")))
            panel.scroll_end(animate=False)
        except Exception as e:
            panel = self.query_one("#messages_panel", ScrollableContainer)
            panel.mount(Static(Align(Panel(
                f"Error al exportar: {e}", 
                title="Error", 
                border_style="red"
            ), align="center")))
            panel.scroll_end(animate=False)
            
    async def action_mostrar_ayuda(self):
        """Muestra información de ayuda sobre comandos y atajos."""
        panel = self.query_one("#messages_panel", ScrollableContainer)
        help_text = """
        ATAJOS DE TECLADO:
        - Ctrl+L: Limpiar historial (borra todo el historial guardado).
        - Ctrl+C: Limpiar pantalla (mantiene el historial guardado).
        - Ctrl+E: Exportar historial a texto plano.
        - Ctrl+H: Mostrar esta ayuda.
        - Ctrl+Q: Salir de la aplicación.
        
        COMANDOS (escribir en el campo de texto):
        - /help o /ayuda: Muestra esta ayuda.
        - /clear o /limpiar: Limpia la pantalla.
        - /clearhistory o /limpiarhistorial: Borra todo el historial.
        - /export o /exportar: Exporta el historial a texto.
        - /mcp on|off: Activa/desactiva Model Context Protocol (experimental).
        """
        panel.mount(Static(Align(Panel(
            help_text, 
            title="Ayuda", 
            border_style="cyan"
        ), align="center")))
        panel.scroll_end(animate=False)
        
    def action_salir(self):
        """Sale de la aplicación TUI."""
        self.exit()
