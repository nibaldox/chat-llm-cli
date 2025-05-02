from textual.app import App, ComposeResult
from textual.containers import Container, ScrollableContainer
from textual.widgets import Header, Footer, Input, Static
from rich.panel import Panel
from rich.align import Align
import asyncio

class ChatApp(App):
    """Textual-based TUI for Chat CLI"""
    TITLE = "Chat LLM TUI"

    def __init__(self, provider, model, stream=False):
        super().__init__()
        self.provider = provider
        self.model = model
        self.stream = stream
        self.history = []
        self.token_count = 0

    def compose(self) -> ComposeResult:
        yield Header()
        yield ScrollableContainer(id="messages_panel")
        yield Input(placeholder="Escribe un mensaje...", id="input_panel")
        yield Footer(Static(f"Tokens: {self.token_count}", id="token_counter"), id="footer")

    async def on_mount(self) -> None:
        # Enfocar input al iniciar
        self.set_focus(self.query_one("#input_panel", Input))

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        text = event.value.strip()
        if not text:
            return
        panel = self.query_one("#messages_panel", ScrollableContainer)
        # Montar mensaje de usuario a la izquierda
        user_widget = Static(Align(Panel(text, title="Tú", border_style="green"), align="left"))
        await panel.mount(user_widget)
        panel.scroll_end(animate=False)
        event.input.value = ""
        # Montar respuesta del modelo en streaming o no
        if self.stream and hasattr(self.provider, "stream_message"):
            resp_widget = Static(Align(Panel("", title="LLM", border_style="blue"), align="right"))
            await panel.mount(resp_widget)
            full_response = ""
            for token in self.provider.stream_message(text):
                self.token_count += 1
                self.query_one("#token_counter", Static).update(f"Tokens: {self.token_count}")
                full_response += token
                resp_widget.update(Align(Panel(full_response, title="LLM", border_style="blue"), align="right"))
                panel.scroll_end(animate=False)
                await asyncio.sleep(0)
            self.history.append(("LLM", full_response))
            panel.scroll_end(animate=False)
        else:
            response = self.provider.send_message(text)
            model_widget = Static(Align(Panel(response, title="LLM", border_style="blue"), align="right"))
            await panel.mount(model_widget)
            panel.scroll_end(animate=False)
            self.token_count += len(response.split())
            self.query_one("#token_counter", Static).update(f"Tokens: {self.token_count}")
            self.history.append(("LLM", response))
