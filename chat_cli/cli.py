import typer
from .providers import get_provider_names
from .providers.openai import OpenAIProvider
from .providers.ollama import OllamaProvider
from .providers.gemini import GeminiProvider
from .providers.anthropic import AnthropicProvider
from .tui import ChatApp
from .history import load_history, save_history, add_message, clear_history, export_history_txt

app = typer.Typer()

@app.command()
def chat(
    provider: str = typer.Option(..., help="Proveedor LLM (openai, gemini, ollama, anthropic)"),
    model: str = typer.Option(None, help="Modelo a usar"),
    stream: bool = typer.Option(False, help="Activar streaming de tokens (si el proveedor lo soporta)"),
    mcp: bool = typer.Option(False, help="Activar Model Context Protocol (solo para Anthropic)")
):
    """Inicia una sesión de chat con el proveedor/modelo seleccionado."""
    typer.echo(f"Chat iniciado con proveedor: {provider}, modelo: {model}")

    # Selección de proveedor
    try:
        if provider == "openai":
            p = OpenAIProvider(model=model or "gpt-3.5-turbo")
        elif provider == "ollama":
            p = OllamaProvider(model=model or "llama2")
        elif provider == "gemini":
            p = GeminiProvider()
        elif provider == "anthropic":
            p = AnthropicProvider(model=model or "claude-3-opus-20240229", mcp_enabled=mcp)
            if mcp:
                typer.echo("Model Context Protocol (M.C.P) activado para Anthropic.")
        else:
            typer.secho("Proveedor no soportado.", fg=typer.colors.RED)
            raise typer.Exit(1)
    except Exception as e:
        typer.secho(f"Error al inicializar el proveedor: {e}", fg=typer.colors.RED)
        raise typer.Exit(1)

    history_file = "history.json"
    history = load_history(history_file)

    # Loop interactivo con manejo de errores y reintentos
    typer.echo("Escribe tu mensaje (o 'exit' para salir):")
    while True:
        prompt = input("Tú: ").strip()
        if prompt.lower() in ("exit", "salir"): 
            typer.echo("Saliendo del chat.")
            break
        add_message(history, "user", prompt)
        respuesta = ""
        max_retries = 2
        for attempt in range(max_retries + 1):
            try:
                if stream and hasattr(p, "stream_message"):
                    typer.echo(f"{provider.capitalize()}: ", nl=False)
                    for token in p.stream_message(prompt):
                        print(token, end="", flush=True)
                        respuesta += token
                    print()
                else:
                    respuesta = p.send_message(prompt)
                    typer.echo(f"{provider.capitalize()}: {respuesta}")
                break  # Éxito, salir del loop de reintentos
            except Exception as e:
                typer.secho(f"Error en el proveedor: {e}", fg=typer.colors.RED)
                if attempt < max_retries:
                    typer.echo("Reintentando...")
                else:
                    respuesta = f"[Error] No se pudo obtener respuesta tras varios intentos."
        add_message(history, provider, respuesta)
        save_history(history, history_file)

@app.command()
def limpiar_historial():
    """Limpia el historial de chat."""
    clear_history("history.json")
    typer.echo("Historial limpiado.")

@app.command()
def exportar_historial_txt(destino: str = typer.Argument("historial.txt")):
    """Exporta el historial a texto plano."""
    try:
        history = load_history("history.json")
        export_history_txt(history, destino)
        typer.echo(f"Historial exportado a {destino}.")
    except FileNotFoundError:
        typer.secho("No se encontró el archivo de historial.", fg=typer.colors.RED)
    except Exception as e:
        typer.secho(f"Error al exportar el historial: {e}", fg=typer.colors.RED)

@app.command()
def tui(
    provider: str = typer.Option(..., help="Proveedor LLM (openai, gemini, ollama, anthropic)"),
    model: str = typer.Option(None, help="Modelo a usar"),
    stream: bool = typer.Option(False, help="Activar streaming de tokens (si el proveedor lo soporta)"),
    mcp: bool = typer.Option(False, help="Activar Model Context Protocol (solo para Anthropic)")
):
    """Inicia la interfaz TUI de chat."""
    typer.echo(f"Iniciando TUI con proveedor: {provider}, modelo: {model}, stream: {stream}")

    # Selección de proveedor (similar a 'chat')
    try:
        if provider == "openai":
            p = OpenAIProvider(model=model or "gpt-3.5-turbo")
        elif provider == "ollama":
            p = OllamaProvider(model=model or "llama2")
        elif provider == "gemini":
            p = GeminiProvider()  # Gemini puede no necesitar modelo específico aquí
        elif provider == "anthropic":
            p = AnthropicProvider(model=model or "claude-3-opus-20240229", mcp_enabled=mcp)
            if mcp:
                typer.echo("Model Context Protocol (M.C.P) activado para Anthropic.")
        else:
            typer.secho("Proveedor no soportado.", fg=typer.colors.RED)
            raise typer.Exit(1)
    except Exception as e:
        typer.secho(f"Error al inicializar el proveedor: {e}", fg=typer.colors.RED)
        raise typer.Exit(1)

    # Crear e iniciar la app TUI
    app_tui = ChatApp(provider=p, model=model, stream=stream)
    app_tui.run()
