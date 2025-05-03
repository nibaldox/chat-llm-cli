# Chat LLM CLI (Ollama, OpenAI, Gemini, Anthropic)

Aplicación de terminal en Python para chatear con modelos LLM vía Ollama, OpenAI, Gemini y Anthropic. Permite historial, streaming, interfaz TUI y soporte para Model Context Protocol (M.C.P).

## Instalación

1. **Clona el repositorio y entra al directorio:**
   ```sh
   git clone <REPO_URL>
   cd 03_chat_LLM
   ```

2. **Crea y activa un entorno virtual:**
   ```sh
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Instala las dependencias:**
   ```sh
   pip install -r requirements.txt
   ```

## Uso básico

### Iniciar chat
```sh
python -m chat_cli chat --provider [openai|ollama|gemini|anthropic] --model <modelo> [--stream] [--mcp]
```
- `--provider`  : Proveedor LLM (`openai`, `ollama`, `gemini`, `anthropic`)
- `--model`     : Modelo a usar (ej: `gpt-3.5-turbo`, `llama2`, `claude-3-opus-20240229`, etc.)
- `--stream`    : (Opcional) Streaming de tokens si el proveedor lo soporta
- `--mcp`       : (Opcional) Activa Model Context Protocol (solo para Anthropic)

### Ejemplos

#### Ollama con streaming

```sh
python -m chat_cli chat --provider ollama --model llama2 --stream
```

#### Anthropic con Model Context Protocol

```sh
python -m chat_cli chat --provider anthropic --model claude-3-opus-20240229 --stream --mcp
```

### Limpiar historial
```sh
python -m chat_cli limpiar-historial
```

### Exportar historial a texto
```sh
python -m chat_cli exportar-historial-txt historial.txt
```

### Interfaz TUI

Para usar la interfaz de texto (TUI) en lugar de la CLI:

```sh
python -m chat_cli tui --provider [openai|ollama|gemini|anthropic] --model <modelo> [--stream] [--mcp]
```

La TUI ofrece las siguientes funcionalidades:
- Historial de mensajes con scroll
- Atajos de teclado (Ctrl+L: limpiar historial, Ctrl+E: exportar, Ctrl+H: ayuda, etc.)
- Comandos de texto (escribir `/help` para ver todos los comandos disponibles)
- Soporte para Model Context Protocol (M.C.P) con Anthropic

## Configuración de claves/API
- **OpenAI**: Define la variable de entorno `OPENAI_API_KEY` o edita el código para tu clave.
- **Gemini**: (Completar integración real según SDK/API de Google).
- **Anthropic**: Define la variable de entorno `ANTHROPIC_API_KEY` o edita el código para tu clave.
- **Ollama**: Requiere Ollama corriendo localmente (`ollama serve`).

## Model Context Protocol (M.C.P)

Esta aplicación incluye soporte para el [Model Context Protocol (M.C.P)](https://modelcontextprotocol.io/introduction) de Anthropic, que permite a los modelos LLM acceder a recursos externos, herramientas y contexto adicional.

Para utilizar M.C.P:

1. Asegúrate de usar el proveedor `anthropic`
2. Activa M.C.P con el parámetro `--mcp`
3. En la TUI, puedes activar/desactivar M.C.P con el comando `/mcp on` o `/mcp off`

Actualmente, la implementación de M.C.P está en fase experimental y se irá mejorando con el tiempo.

## Pruebas

1. **Ejecutar tests unitarios:**
   ```sh
   PYTHONPATH=. pytest tests
   ```

## Estructura del Proyecto
```
03_chat_LLM/
├── chat_cli/
│   ├── __main__.py
│   ├── cli.py
│   ├── history.py
│   └── providers/
│       ├── openai.py
│       ├── ollama.py
│       └── gemini.py
├── requirements.txt
├── PLAN_IMPLEMENTACION.md
├── RDP_PROYECTO.md
├── README.md
└── tests/
    ├── test_history.py
    └── test_providers.py
```

## Notas
- El historial se guarda automáticamente en `history.json`.
- Puedes extender fácilmente añadiendo más proveedores en `chat_cli/providers/`.
- Si tienes dudas o errores, revisa el archivo `PLAN_IMPLEMENTACION.md` para ver el estado y fases del proyecto.

---

Desarrollado por [Tu Nombre].
