from textual.app import App, ComposeResult
from textual.containers import Container, ScrollableContainer
from textual.widgets import Header, Footer, Input, Static
from textual.binding import Binding
from rich.panel import Panel
from rich.align import Align
from rich.markdown import Markdown
import asyncio
import os
import time
from datetime import datetime
from .history import load_history, save_history, clear_history, export_history_txt
from textual.reactive import reactive

# Archivo de historial por defecto
HIST_FILE = "history.json"
EXPORT_FILE = "historial.txt"

# Constantes para Model Context Protocol
MCP_ENABLED = False  # Activar cuando se implemente completamente

class ChatApp(App):
    """Textual-based TUI para Chat CLI con historial, atajos y mejoras visuales."""
    
    TITLE = "Chat LLM TUI"
    CSS = """
    App {
        background: black;
        color: white;
    }
    Header {
        background: black;
        color: white;
        text-style: bold;
        height: 1; /* Ensure header is compact */
    }
    Footer {
        background: black;
        color: grey; /* Less emphasis for footer text */
        height: 1; /* Ensure footer is compact */
    }
    Input {
        background: rgb(30,30,30);
        color: white;
        border: round grey;
    }
    Input:focus {
        border: round cyan;
    }
    ScrollableContainer#messages_panel {
        background: black;
    }
    Static#status_text {
        background: black;
        color: grey;       /* Default text to grey for labels */
        dock: bottom;
        height: 1;
        padding: 0 1;      /* Add padding */
    }
    /* Styling for user messages */
    Panel { /* Default Panel styling, can be overridden by specific classes */
        padding: 0 1; /* Add some horizontal padding to all panels */
    }
    Static.user_message Panel {
        border: round cyan; /* Combined border-style and border_foreground */
    }
    Static.llm_message Panel {
        border: round blue;
    }
    Static.llm_message Markdown { /* Default text color for markdown inside LLM panels */
        color: white;
    }
    Static.llm_message Markdown code_block { /* Markdown code blocks */
        background: rgb(35,35,40);
        color: #AFEEEE; /* PaleTurquoise */
        padding: 1 2;
        border: round rgb(60,60,60);
    }
    Static.llm_message Markdown code { /* Inline code */
        background: rgb(50,50,50);
        color: #AFEEEE; /* PaleTurquoise */
        padding: 0 1;
    }
    Static.llm_message Markdown b, Static.llm_message Markdown strong { /* Bold text */
        color: #FFFFE0; /* LightYellow */
        text-style: bold;
    }
    Static.llm_message Markdown a { /* Links */
        color: #ADD8E6; /* LightBlue */
        text-style: underline;
    }
    Static.llm_message Markdown h1, Static.llm_message Markdown h2, Static.llm_message Markdown h3 {
        text-style: bold;
        color: #ADD8E6; /* LightBlue for headings */
    }
    Static.info_message Panel {
        border: round grey;
    }
    Static.error_message Panel {
        border: round red;
    }
    Static.help_message Panel { /* Specific style for help panel border */
        border: round #00FFFF; /* Cyan border for help */
    }
    /* Note: Styling panel titles directly with CSS (e.g., .user_message .panel--title)
       is unreliable with Rich Panels in Textual. Titles are styled with BBCode in Python. */
    """
    BINDINGS = [
        Binding("ctrl+l", "limpiar_historial", "Limpiar historial"),
        Binding("ctrl+e", "exportar_historial", "Exportar historial"),
        Binding("ctrl+c", "limpiar_pantalla", "Limpiar pantalla"),
        Binding("ctrl+h", "mostrar_ayuda", "Mostrar ayuda"),
        Binding("ctrl+q", "salir", "Salir")
    ]

    # Reactive attributes auto-update UI
    status_text: str = reactive("")
    history: list = reactive([])
    token_count: int = reactive(0)
    tokens_per_second: float = reactive(0.0)

    def __init__(self, provider, model, stream=False):
        """Inicializa la aplicación TUI con el proveedor y modelo seleccionados."""
        super().__init__()
        # Evitar que watch_history se ejecute durante inicialización
        self._initializing = True
        self.provider = provider
        self.model = model
        self.stream = stream
        # reactive history will load on mount
        self.token_count = 0
        self.tokens_per_second = 0.0
        self.start_time = 0.0
        self.last_token_time = 0.0
        self.last_activity = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.mcp_enabled = MCP_ENABLED
        # Prepare initial status (para asignar tras montaje)
        self._initial_status_text = f"Modelo: {model} | Tokens: 0 | TPS: 0.0 | Streaming: {'Activado' if stream else 'Desactivado'} | MCP: {'Activado' if self.mcp_enabled else 'Desactivado'}"

    def load_and_show_history(self):
        """Carga el historial desde archivo y lo muestra en la TUI al iniciar."""
        # Carga reactiva de historial; la UI se actualizará en watch_history
        try:
            self.history = load_history(HIST_FILE)
            if not self.history: # Ensure history is not None if file was empty/corrupt
                self.history = []
        except Exception:
            self.history = []

    def compose(self) -> ComposeResult:
        """Define la estructura de la interfaz de usuario."""
        yield Header()
        yield ScrollableContainer(id="messages_panel")
        yield Input(placeholder="Escribe un mensaje... (Ctrl+H para ayuda)", id="input_panel")
        yield Footer()
        yield Static(self.status_text, id="status_text")

    async def on_mount(self) -> None:
        """Se ejecuta al montar la aplicación."""
        self.set_focus(self.query_one("#input_panel", Input))
        # Limpiar panel al iniciar
        panel = self.query_one("#messages_panel", ScrollableContainer)
        widgets_to_remove = list(panel.children)
        for widget in widgets_to_remove:
            widget.remove()
        # Mensaje de bienvenida
        panel.mount(Static(Align(Panel(
            "Chat limpio. Escribe /loadhistory para ver chats anteriores.", title="[bold grey]Info[/]"
        ), align="center"), classes="info_message")) # Added class for styling
        # Set initial status_text
        self.status_text = self._initial_status_text
        # Load history after UI listo
        self.load_and_show_history()
        # Montaje completado
        self._initializing = False

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
            
        # Guardar usuario en historial; UI se actualiza en watch_history
        self.last_activity = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.history = self.history + [{"role": "user", "content": text, "timestamp": self.last_activity}]
        save_history(self.history, HIST_FILE)
        # Mostrar mensaje del usuario inmediatamente
        panel = self.query_one("#messages_panel", ScrollableContainer)
        # Using Rich BBCode for title color as CSS targeting panel titles is unreliable
        user_widget = Static(Align(Panel(text, title=f"[bold #00FFFF]Tú[/] [{self.last_activity}]"), align="left"), classes="user_message")
        await panel.mount(user_widget)
        panel.scroll_end(animate=False)
        event.input.value = ""
        
        # Actualizar última actividad
        self.last_activity = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Montar respuesta del modelo en streaming o no
        try:
            # Mostrar indicador de "pensando..."
            thinking_widget = Static(Align(Panel(
                "Pensando...", 
                title="[bold grey]Estado[/]" # Styled title
            ), align="center"), classes="info_message") # Added class
            panel = self.query_one("#messages_panel", ScrollableContainer)
            await panel.mount(thinking_widget)
            panel.scroll_end(animate=False)
            
            if self.stream and hasattr(self.provider, "stream_message"):
                # Eliminar indicador de pensando
                thinking_widget.remove()
                
                # Crear widget para respuesta en streaming
                timestamp = datetime.now().strftime("%H:%M:%S")
                # Using Rich BBCode for title color
                resp_widget = Static(Align(Panel(
                    "", 
                    title=f"[bold #ADD8E6]LLM[/] [{timestamp}]" # LightBlue for LLM title
                ), align="right"), classes="llm_message")
                await panel.mount(resp_widget)
                
                # Iniciar conteo de tokens por segundo
                self.start_time = time.time()
                self.last_token_time = self.start_time
                tokens_in_window = 0
                time_window = 1.0  # Ventana de 1 segundo para calcular TPS
                
                # Procesar tokens en streaming
                full_response = ""
                batch_tokens = []
                flush_interval = 0.2  # segundos
                last_flush = time.time()
                for token in self.provider.stream_message(text):
                    current_time = time.time()
                    self.token_count += 1
                    tokens_in_window += 1
                    
                    # Calcular tokens por segundo en la ventana actual
                    elapsed = current_time - self.last_token_time
                    if elapsed >= time_window:
                        self.tokens_per_second = tokens_in_window / elapsed
                        self.last_token_time = current_time
                        tokens_in_window = 0
                    
                    full_response += token
                    batch_tokens.append(token)
                    # Flush si alcanza tamaño o intervalo
                    if len(batch_tokens) >= 5 or (current_time - last_flush) >= flush_interval:
                        from rich.markdown import Markdown
                        resp_widget.update(Align(Panel(
                            Markdown(full_response), # Markdown content
                            title=f"[bold #ADD8E6]LLM[/] [{timestamp}]" # Keep title styled
                        ), align="right"))
                        panel.scroll_end(animate=False)
                        self._update_status_bar()
                        batch_tokens.clear()
                        last_flush = current_time
                    await asyncio.sleep(0)
                
                # Calcular TPS final
                total_time = time.time() - self.start_time
                if total_time > 0:
                    self.tokens_per_second = len(full_response) / total_time
                
                # Flush final de tokens restantes
                if batch_tokens:
                    from rich.markdown import Markdown
                    resp_widget.update(Align(Panel(
                        Markdown(full_response), # Markdown content
                        title=f"[bold #ADD8E6]LLM[/] [{timestamp}]" # Keep title styled
                    ), align="right"))
                    panel.scroll_end(animate=False)
                
                # Guardar asistente en historial; UI se actualiza en watch_history
                ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.history = self.history + [{"role": "assistant", "content": full_response, "timestamp": ts}]
                save_history(self.history, HIST_FILE)
            else:
                # Obtener respuesta completa
                response = self.provider.send_message(text)
                
                # Eliminar indicador de pensando
                thinking_widget.remove()
                
                # Guardar asistente en historial; UI se actualiza en watch_history
                self.token_count += len(response.split())
                self._update_status_bar()
                ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                # Render assistant message directly, now with Markdown for consistency
                assistant_widget = Static(Align(Panel(
                    Markdown(response), # Render as Markdown
                    title=f"[bold #ADD8E6]LLM[/] [{ts}]"
                ), align="right"), classes="llm_message")
                await panel.mount(assistant_widget)
                panel.scroll_end(animate=False)

                self.history = self.history + [{"role": "assistant", "content": response, "timestamp": ts}]
                save_history(self.history, HIST_FILE)
        except Exception as e:
            # Manejar errores
            if 'thinking_widget' in locals():
                thinking_widget.remove()
            error_msg = f"[Error] {e}"
            panel = self.query_one("#messages_panel", ScrollableContainer)
            await panel.mount(Static(Align(Panel(
                error_msg, 
                title="[bold red]Error[/]" # Styled title
            ), align="center"), classes="error_message"))
            panel.scroll_end(animate=False)

    async def _process_command(self, text):
        """Procesa comandos especiales que comienzan con /."""
        panel = self.query_one("#messages_panel", ScrollableContainer)
        command = text.lower().strip()
        
        if command in ("/help", "/ayuda"):
            await self.action_mostrar_ayuda()
        elif command in ("/clear", "/limpiar"):
            await self.action_limpiar_pantalla()
        elif command in ("/clearhistory", "/limpiarhistorial"):
            await self.action_limpiar_historial()
        elif command in ("/export", "/exportar"):
            await self.action_exportar_historial()
        elif command.startswith("/loadhistory") or command.startswith("/cargarhistorial"):
            self.load_and_show_history()
            self._update_status_bar()
        elif command.startswith("/mcp"):
            mcp_info_title = "[bold grey]Info MCP[/]"
            if " on" in command or " activar" in command:
                self.mcp_enabled = True
                await panel.mount(Static(Align(Panel(
                    "Model Context Protocol activado", 
                    title=mcp_info_title
                ), align="center"), classes="info_message"))
            elif " off" in command or " desactivar" in command:
                self.mcp_enabled = False
                await panel.mount(Static(Align(Panel(
                    "Model Context Protocol desactivado", 
                    title=mcp_info_title
                ), align="center"), classes="info_message"))
            else:
                await panel.mount(Static(Align(Panel(
                    "Uso: /mcp on|off o /mcp activar|desactivar", 
                    title=mcp_info_title
                ), align="center"), classes="info_message"))
            self._update_status_bar()
        else:
            await panel.mount(Static(Align(Panel(
                f"Comando desconocido: {text}. Escribe /help para ver los comandos disponibles.", 
                title="[bold grey]Info[/]"
            ), align="center"), classes="info_message"))
        panel.scroll_end(animate=False)
        
    def _update_status_bar(self):
        """Actualiza la barra de estado con información actualizada usando Rich BBCode."""
        dim_color = "#9E9E9E"  # Grey for labels
        value_color = "#D0D0D0" # Light grey for values
        separator = f"[{dim_color}]|[/]"

        model_str = f"[{dim_color}]Modelo:[/] [{value_color}]{self.model}[/]"
        tokens_str = f"[{dim_color}]Tokens:[/] [{value_color}]{self.token_count}[/]"
        tps_str = f"[{dim_color}]TPS:[/] [{value_color}]{self.tokens_per_second:.1f}[/]"

        stream_status_text = "Activado" if self.stream else "Desactivado"
        stream_color = "green" if self.stream else "red"
        stream_str = f"[{dim_color}]Streaming:[/] [{stream_color}]{stream_status_text}[/]"

        mcp_status_text = "Activado" if self.mcp_enabled else "Desactivado"
        mcp_color = "green" if self.mcp_enabled else "red"
        mcp_str = f"[{dim_color}]MCP:[/] [{mcp_color}]{mcp_status_text}[/]"

        self.status_text = f"{model_str} {separator} {tokens_str} {separator} {tps_str} {separator} {stream_str} {separator} {mcp_str}"

    async def action_limpiar_historial(self):
        """Limpia el historial de la sesión y del archivo."""
        clear_history(HIST_FILE)
        # Reset reactive properties
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
            title="[bold grey]Info[/]"
        ), align="center"), classes="info_message"))
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
            title="[bold grey]Info[/]"
        ), align="center"), classes="info_message"))
        panel.scroll_end(animate=False)
        
    async def action_exportar_historial(self):
        """Exporta el historial a un archivo de texto plano."""
        try:
            export_history_txt(self.history, EXPORT_FILE)
            panel = self.query_one("#messages_panel", ScrollableContainer)
            panel.mount(Static(Align(Panel(
                f"Historial exportado a {EXPORT_FILE}", 
                title="[bold grey]Info[/]"
            ), align="center"), classes="info_message"))
            panel.scroll_end(animate=False)
        except Exception as e:
            panel = self.query_one("#messages_panel", ScrollableContainer)
            panel.mount(Static(Align(Panel(
                f"Error al exportar: {e}", 
                title="[bold red]Error[/]"
            ), align="center"), classes="error_message"))
            panel.scroll_end(animate=False)
            
    async def action_mostrar_ayuda(self):
        """Muestra información de ayuda sobre comandos y atajos."""
        panel = self.query_one("#messages_panel", ScrollableContainer)
        help_text = """
        [bold]ATAJOS DE TECLADO:[/bold]
        - Ctrl+L: Limpiar historial (borra todo el historial guardado).
        - Ctrl+C: Limpiar pantalla (mantiene el historial guardado).
        - Ctrl+E: Exportar historial a texto plano.
        - Ctrl+H: Mostrar esta ayuda.
        - Ctrl+Q: Salir de la aplicación.

        [bold]COMANDOS (escribir en el campo de texto):[/bold]
        - /help o /ayuda: Muestra esta ayuda.
        - /clear o /limpiar: Limpia la pantalla.
        - /clearhistory o /limpiarhistorial: Borra todo el historial.
        - /export o /exportar: Exporta el historial a texto.
        - /loadhistory o /cargarhistorial: Carga chats anteriores guardados.
        - /mcp on|off: Activa/desactiva Model Context Protocol (experimental).
        """
        # Help panel uses its own class for specific border color
        panel.mount(Static(Align(Panel(
            help_text, 
            title="[bold #00FFFF]Ayuda[/]" # Cyan for Help title, matches border
        ), align="center"), classes="help_message"))
        panel.scroll_end(animate=False)
        
    def action_salir(self):
        """Sale de la aplicación TUI."""
        self.exit()

    def watch_status_text(self, new_text: str) -> None:
        # Omitir antes de completar montaje
        if getattr(self, '_initializing', True):
            return
        try:
            self.query_one("#status_text", Static).update(new_text)
        except Exception:
            return

    def watch_history(self, new_history: list) -> None:
        # No-op: History rendering is handled by on_input_submitted and load_and_show_history
        # If we want reactive history display, this is where it would go.
        if self._initializing: # Avoid updates during setup
            return

        # Example of how reactive history display could work (currently not fully used for messages):
        # panel = self.query_one("#messages_panel", ScrollableContainer)
        # for child in panel.children: # Clear existing messages if redrawing all
        #     child.remove()
        # for message in new_history:
        #     # This part would need to replicate the styling logic from on_input_submitted
        #     # and _render_message_widget or similar helper.
        #     # For simplicity, current implementation mounts messages directly.
        #     pass
        return
