# Chat LLM CLI (Ollama, OpenAI, Gemini)

Aplicación de terminal en Python para chatear con modelos LLM vía Ollama, OpenAI y Gemini. Permite historial, streaming y es fácilmente extensible.

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
python -m chat_cli chat --provider [openai|ollama|gemini] --model <modelo> [--stream]
```
- `--provider`  : Proveedor LLM (`openai`, `ollama`, `gemini`)
- `--model`     : Modelo a usar (ej: `gpt-3.5-turbo`, `llama2`, etc.)
- `--stream`    : (Opcional) Streaming de tokens si el proveedor lo soporta

### Ejemplo por defecto (Ollama):
```sh
python -m chat_cli chat --provider ollama --model llama2 --stream
```

### Limpiar historial
```sh
python -m chat_cli limpiar-historial
```

### Exportar historial a texto
```sh
python -m chat_cli exportar-historial-txt historial.txt
```

## Configuración de claves/API
- **OpenAI**: Define la variable de entorno `OPENAI_API_KEY` o edita el código para tu clave.
- **Gemini**: (Completar integración real según SDK/API de Google)
- **Ollama**: Requiere Ollama corriendo localmente (`ollama serve`)

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
