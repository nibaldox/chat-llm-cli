import typer
from .providers import get_provider_names
from .providers.openai import OpenAIProvider
from .providers.ollama import OllamaProvider
from .providers.gemini import GeminiProvider
from .providers.anthropic import AnthropicProvider
from .tui import ChatApp
from .history import load_history, save_history, add_message, clear_history, export_history_txt
from rich.console import Console
from rich.markdown import Markdown
from rich.prompt import Prompt, Confirm 
from rich.panel import Panel 
import sys 

console = Console()
app = typer.Typer(add_completion=False) 

# --- Helper Functions --- 

def _get_provider_instance(provider_name: str, model: str = None, stream: bool = False, mcp: bool = False):
    """Initializes and returns a provider instance."""
    try:
        if provider_name == "openai":
            return OpenAIProvider(model=model or "gpt-3.5-turbo")
        elif provider_name == "ollama":
            return OllamaProvider(model=model or "llama2") 
        elif provider_name == "gemini":
            return GeminiProvider() 
        elif provider_name == "anthropic":
            anth_provider = AnthropicProvider(model=model or "claude-3-opus-20240229", mcp_enabled=mcp)
            if mcp:
                console.print("Model Context Protocol (M.C.P) activado para Anthropic.")
            return anth_provider
        else:
            console.print(f"Proveedor '{provider_name}' no soportado.", style="red")
            raise typer.Exit(1)
    except Exception as e:
        console.print(f"Error al inicializar el proveedor {provider_name}: {e}", style="red")
        raise typer.Exit(1)

def _run_chat_session(provider_instance, provider_name: str, stream: bool):
    """Runs the simple command-line chat session."""
    history_file = "history.json"
    history = load_history(history_file)

    console.print(Panel(f"Chat iniciado con [bold]{provider_name.capitalize()}[/bold]. Modelo: [bold]{provider_instance.model}[/bold]. Escribe 'exit' o 'salir' para terminar.", title="[green]Sesión de Chat[/green]"))
    while True:
        prompt_text = Prompt.ask("[cyan]Tú[/cyan]")
        if prompt_text.lower() in ("exit", "salir"): 
            console.print("Saliendo del chat.")
            break
        
        add_message(history, "user", prompt_text)
        respuesta = ""
        max_retries = 2 

        with console.status("[yellow]Pensando...[/yellow]", spinner="dots"):
            for attempt in range(max_retries + 1):
                try:
                    if stream and hasattr(provider_instance, "stream_message"):
                        console.print(f"[bold]{provider_name.capitalize()}:[/bold] ", end="")
                        current_line_tokens = []
                        for token in provider_instance.stream_message(prompt_text):
                            print(token, end="", flush=True)
                            respuesta += token
                            current_line_tokens.append(token)
                            if "\n" in token:
                                console.print(f"[bold]{provider_name.capitalize()}:[/bold] ", end="") 
                        print() 
                    else:
                        respuesta = provider_instance.send_message(prompt_text)
                        console.print(f"[bold]{provider_name.capitalize()}:[/bold]")
                        console.print(Markdown(respuesta))
                    break  
                except Exception as e:
                    console.print(f"Error en el proveedor: {e}", style="red")
                    if attempt < max_retries:
                        console.print("Reintentando...")
                    else:
                        respuesta = f"[Error] No se pudo obtener respuesta tras varios intentos."
                        console.print(Markdown(respuesta), style="red")
        
        add_message(history, provider_name, respuesta)
        save_history(history, history_file)

def _run_tui_session(provider_instance, model: str, stream: bool):
    """Runs the Text User Interface (TUI) chat session."""
    app_tui = ChatApp(provider=provider_instance, model=model, stream=stream) 
    app_tui.run()

# --- Typer Commands --- 

@app.command()
def chat(
    provider: str = typer.Option(..., "-p", "--provider", help="Proveedor LLM (ollama, gemini, openai, anthropic)", rich_help_panel="Configuración del Chat"),
    model: str = typer.Option(None, "-m", "--model", help="Modelo a usar (opcional)", rich_help_panel="Configuración del Chat"),
    stream: bool = typer.Option(False, "-s", "--stream", help="Activar streaming de tokens", rich_help_panel="Configuración del Chat"),
    mcp: bool = typer.Option(False, "--mcp", help="Activar Model Context Protocol (Anthropic)", rich_help_panel="Configuración del Chat")
):
    """Inicia una sesión de chat TUI con el proveedor/modelo especificado."""
    p_instance = _get_provider_instance(provider, model, stream, mcp)
    _run_tui_session(p_instance, model or p_instance.model, stream) # Pass model for TUI, can be p_instance.model if not specified

@app.command()
def limpiar_historial():
    """Limpia el historial de chat."""
    clear_history("history.json")
    console.print("[green]Historial limpiado exitosamente.[/green]")

@app.command()
def exportar_historial_txt(destino: str = typer.Argument("historial.txt", help="Archivo de destino para la exportación.")):
    """Exporta el historial a un archivo de texto plano."""
    try:
        history = load_history("history.json")
        export_history_txt(history, destino)
        console.print(f"[green]Historial exportado a {destino}.[/green]")
    except FileNotFoundError:
        console.print("[red]No se encontró el archivo de historial.[/red]")
    except Exception as e:
        console.print(f"[red]Error al exportar el historial: {e}[/red]")

@app.command()
def tui(
    provider: str = typer.Option(..., "-P", "--provider-tui", help="Proveedor LLM para TUI", rich_help_panel="Configuración TUI"), 
    model: str = typer.Option(None, "-M", "--model-tui", help="Modelo a usar en TUI (opcional)", rich_help_panel="Configuración TUI"),
    stream: bool = typer.Option(False, "-S", "--stream-tui", help="Activar streaming en TUI", rich_help_panel="Configuración TUI"),
    mcp: bool = typer.Option(False, "--mcp-tui", help="Activar MCP en TUI (Anthropic)", rich_help_panel="Configuración TUI")
):
    """Inicia la interfaz TUI de chat."""
    console.print(Panel(f"Iniciando TUI con proveedor: [bold]{provider}[/bold], modelo: [bold]{model or 'default'}[/bold], stream: {stream}", title="[blue]Interfaz TUI[/blue]"))
    p_instance = _get_provider_instance(provider, model, stream, mcp)
    _run_tui_session(p_instance, model or p_instance.model, stream) 

# --- New Default TUI Flow --- 

def _select_chat_options():
    """Handles interactive selection of provider, model, and other chat options."""
    console.print(Panel("[bold green]Configuración de la Sesión de Chat TUI[/bold green]", expand=False))

    available_providers = get_provider_names()
    if not available_providers:
        console.print("[red]No hay proveedores configurados. Saliendo.[/red]")
        raise typer.Exit(1)
        
    provider_name = Prompt.ask(
        "Selecciona un proveedor LLM",
        choices=available_providers,
        default=available_providers[0]
    )

    model_name = None
    if provider_name == "ollama":
        console.print("Detectando modelos locales de Ollama...")
        local_models = OllamaProvider.list_local_models()
        if local_models:
            choices = local_models + ["(Ingresar manualmente)"]
            model_name = Prompt.ask(
                "Selecciona un modelo de Ollama",
                choices=choices,
                default=local_models[0]
            )
            if model_name == "(Ingresar manualmente)":
                model_name = Prompt.ask("Ingresa el nombre del modelo Ollama", default=OllamaProvider().model)
        else:
            console.print("No se detectaron modelos locales de Ollama o hubo un error.")
            model_name = Prompt.ask("Ingresa el nombre del modelo Ollama", default=OllamaProvider().model)
    elif provider_name == "openai":
        model_name = Prompt.ask("Ingresa el nombre del modelo OpenAI", default=OpenAIProvider().model)
    elif provider_name == "anthropic":
        model_name = Prompt.ask("Ingresa el nombre del modelo Anthropic", default=AnthropicProvider().model)
    # Gemini might not require a model name, or add prompt if needed

    stream_chat = Confirm.ask("¿Activar streaming de tokens?", default=False)
    mcp_chat = False
    if provider_name == "anthropic":
        mcp_chat = Confirm.ask("¿Activar Model Context Protocol (M.C.P)?", default=False)

    return provider_name, model_name, stream_chat, mcp_chat

def start_default_tui():
    """Configures and starts the TUI session by default."""
    console.print(Panel("[bold magenta]Bienvenido al Asistente de Chat CLI[/bold magenta]", title="ChatLLM CLI - TUI Mode", expand=False))
    provider_name, model_name, stream_chat, mcp_chat = _select_chat_options()
    
    selected_model_name = model_name
    display_model_name = model_name or "default"

    console.print(f"\nIniciando TUI con Proveedor: [bold]{provider_name}[/bold], Modelo: [bold]{display_model_name}[/bold], Stream: {stream_chat}, MCP: {mcp_chat}")
    provider_instance = _get_provider_instance(provider_name, selected_model_name, stream_chat, mcp_chat)
    _run_tui_session(provider_instance, selected_model_name or provider_instance.model, stream_chat)

# --- Interactive Menu (Now for other utilities) --- 

@app.command(name="menu") # Make it an explicit command
def interactive_menu_command(ctx: typer.Context):
    """Muestra el menú interactivo para utilidades adicionales."""
    interactive_menu_logic(ctx)

def interactive_menu_logic(ctx: typer.Context):
    console.print(Panel("[bold magenta]Asistente de Chat CLI - Utilidades[/bold magenta]", title="ChatLLM CLI", expand=False))

    while True:
        console.print("\n[bold]Menú de Utilidades:[/bold]")
        action = Prompt.ask(
            "¿Qué te gustaría hacer?",
            choices=["Limpiar Historial", "Exportar Historial", "Salir"],
            default="Limpiar Historial" # Changed default
        )

        if action == "Limpiar Historial":
            limpiar_historial()
        elif action == "Exportar Historial":
            export_dest = Prompt.ask("Nombre del archivo para exportar el historial", default="historial_exportado.txt")
            exportar_historial_txt(export_dest)
        elif action == "Salir":
            console.print("[bold blue]¡Hasta luego![/bold blue]")
            break

@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """
    ChatLLM CLI: Habla con diferentes LLMs desde tu terminal.
    Por defecto, inicia la TUI con un menú de selección previo.
    Usa 'menu' para acceder a otras utilidades.
    """
    if ctx.invoked_subcommand is None:
        start_default_tui() # Changed default action
    # else: Typer handles the subcommand call

if __name__ == "__main__":
    app() # Simplified: Typer handles everything
