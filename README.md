# Chat LLM CLI (Ollama, OpenAI, Gemini, Anthropic)

Aplicación de terminal en Python para chatear con modelos LLM vía Ollama, OpenAI, Gemini y Anthropic. Permite historial, streaming, interfaz TUI y soporte para Model Context Protocol (M.C.P).

## Instalación

1. **Clona el repositorio y entra al directorio:**
   ```sh
   git clone <URL_DEL_REPOSITORIO_AQUI> # Asegúrate de reemplazar esto con la URL real de tu repositorio
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

## Uso Principal

La aplicación ahora inicia por defecto en una Interfaz de Usuario de Texto (TUI) que te permite seleccionar el proveedor, el modelo y otras opciones antes de comenzar a chatear.

**Iniciar la Aplicación:**

Simplemente ejecuta el módulo `chat_cli` desde la raíz del proyecto:

```sh
python -m chat_cli
```

Al iniciar, se te presentará un menú dentro de la TUI para:
1.  Seleccionar el **Proveedor LLM** (Ollama, OpenAI, Gemini, Anthropic).
2.  Seleccionar el **Modelo**:
    *   Para **Ollama**, se listarán automáticamente los modelos que tengas instalados localmente.
    *   Para **OpenAI**, la aplicación intentará listar los modelos compatibles más comunes (ej. "gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"). Podrás seleccionar uno de la lista o elegir ingresar un nombre de modelo manualmente.
    *   Para otros proveedores (Gemini, Anthropic), podrás ingresar el nombre del modelo directamente.
3.  Configurar opciones adicionales como **Streaming** de tokens y **Model Context Protocol (MCP)** para Anthropic.

Una vez configurado, presiona "Iniciar Chat" para comenzar tu sesión en la TUI.

### Funcionalidades de la TUI

La TUI ofrece una experiencia de chat mejorada con:

*   Historial de mensajes interactivo con scroll.
*   Carga de historial anterior con el comando `/loadhistory`.
*   Métricas de rendimiento como tokens por segundo (TPS) en la barra de estado.
*   Atajos de teclado:
    *   `Ctrl+L`: Limpiar historial (borra el archivo `history.json`).
    *   `Ctrl+C`: Limpiar solo la pantalla actual (mantiene el historial).
    *   `Ctrl+E`: Exportar el historial de la sesión actual a un archivo de texto (`historial.txt` por defecto).
    *   `Ctrl+H`: Mostrar la ayuda con comandos y atajos.
    *   `Ctrl+Q`: Salir de la aplicación.
*   Comandos de texto (escribir en el campo de mensaje y presionar Enter):
    *   `/help` o `/ayuda`: Muestra la ayuda.
    *   `/clear` o `/limpiar`: Limpia la pantalla actual.
    *   `/clearhistory` o `/limpiarhistorial`: Borra todo el historial (archivo y sesión).
    *   `/export` o `/exportar`: Exporta el historial de la sesión a texto.
    *   `/loadhistory` o `/cargarhistorial`: Carga y muestra el historial guardado en `history.json`.
    *   `/mcp on|off`: Activa o desactiva el Model Context Protocol (si el proveedor lo soporta, principalmente Anthropic).

### Otras Operaciones desde la Línea de Comandos

Aunque el uso principal es a través de la TUI interactiva, algunas operaciones aún pueden realizarse directamente:

**1. Iniciar Chat TUI con Parámetros (Omitiendo Selección Inicial):**

Si deseas iniciar la TUI directamente con una configuración específica, puedes usar:

```sh
# Para la TUI directamente (ahora es el comportamiento del comando 'chat' también)
python -m chat_cli tui --provider-tui [openai|ollama|gemini|anthropic] --model-tui <modelo> [--stream-tui] [--mcp-tui]

# Ejemplo con Ollama:
python -m chat_cli tui --provider-tui ollama --model-tui llama2 --stream-tui
```

El comando `chat` también se comporta de esta manera si se le pasan argumentos:
```sh
python -m chat_cli chat --provider ollama --model llama2 --stream
```

**2. Menú de Utilidades:**

Para acceder a opciones como limpiar o exportar el historial sin iniciar un chat:
```sh
python -m chat_cli menu
```
Este menú te permitirá:
*   Limpiar el historial (`history.json`).
*   Exportar el historial a un archivo de texto.

**3. Limpiar el Historial Directamente:**
```sh
python -m chat_cli limpiar-historial
```

**4. Exportar el Historial Directamente:**
```sh
python -m chat_cli exportar-historial-txt nombre_del_archivo.txt
```

## Configuración Avanzada: `config.yaml`

Esta aplicación utiliza un archivo `config.yaml` en la raíz del proyecto para gestionar de forma centralizada las claves API y los modelos por defecto para cada proveedor. Este método es ahora la forma principal de configurar el acceso a los proveedores.

**Prioridad de Configuración:**

La aplicación utiliza la siguiente jerarquía para determinar la configuración (de mayor a menor prioridad):
1.  Parámetros directos pasados por línea de comandos (ej: `--model mi_modelo_especifico`).
2.  Valores definidos en el archivo `config.yaml`.
3.  Variables de entorno del sistema (ej: `OPENAI_API_KEY`).
4.  Valores por defecto codificados en la aplicación.

**Creación y Estructura de `config.yaml`:**

Debes crear este archivo manualmente en la raíz del proyecto (`03_chat_LLM/config.yaml`).

Aquí tienes un ejemplo de su estructura:

```yaml
# Ejemplo de config.yaml

# Claves API
openai_api_key: "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
anthropic_api_key: "sk-ant-xxxxxxxxxxxxxxxxxxxxxxxxxxxx"
gemini_api_key: "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
# Ollama no requiere clave API por defecto, pero podrías añadir configuraciones futuras aquí.

# Modelos por defecto (opcional, si no se especifican se usarán los predeterminados por el proveedor)
default_openai_model: "gpt-4-turbo-preview"
default_anthropic_model: "claude-3-opus-20240229"
default_gemini_model: "gemini-pro"
default_ollama_model: "llama2"

# Otras configuraciones específicas del proveedor (ejemplo)
# ollama_host: "http://localhost:11434" # Si necesitas personalizar el host de Ollama
```

**Notas Importantes:**
*   **OpenAI**: Define `openai_api_key` en `config.yaml` o la variable de entorno `OPENAI_API_KEY`.
*   **Anthropic**: Define `anthropic_api_key` en `config.yaml` o la variable de entorno `ANTHROPIC_API_KEY`.
*   **Gemini**: Define `gemini_api_key` en `config.yaml` o la variable de entorno `GEMINI_API_KEY`. La integración con Gemini está completamente funcional.
*   **Ollama**: Por lo general, no requiere una clave API. Asegúrate de que el servicio de Ollama esté ejecutándose localmente (ej: `ollama serve`). Puedes especificar `default_ollama_model` en `config.yaml`.

**Seguridad:** El archivo `config.yaml` está incluido en `.gitignore` por defecto para evitar que subas tus claves API accidentalmente a un repositorio. **No elimines esta entrada de `.gitignore` si tu repositorio es público o compartido.**

## Model Context Protocol (M.C.P)

Esta aplicación incluye soporte para el [Model Context Protocol (M.C.P)](https://modelcontextprotocol.io/introduction), principalmente para modelos de Anthropic. Este protocolo permite a los modelos LLM acceder a recursos externos, herramientas y contexto adicional.

*   **Activación**: Puedes activar MCP durante la selección de opciones al inicio de la TUI si eliges Anthropic como proveedor.
*   **Comando en TUI**: Dentro de la TUI, puedes usar `/mcp on` o `/mcp off` para activar o desactivar MCP dinámicamente (si el proveedor lo soporta).

El soporte de M.C.P sigue siendo experimental y se refinará.

## Pruebas

1. **Ejecutar tests unitarios:**
   ```sh
   PYTHONPATH=. pytest tests
   ```

## Estructura del Proyecto
```
03_chat_LLM/
├── chat_cli/
│   ├── __init__.py
│   ├── __main__.py
│   ├── cli.py
│   ├── config.py
│   ├── history.py
│   ├── tui.py  # Contiene la lógica de la Interfaz de Usuario de Texto
│   └── providers/
│       ├── __init__.py
│       ├── anthropic.py
│       ├── gemini.py
│       ├── ollama.py
│       └── openai.py
├── config.yaml
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

creado por N.A.V.
