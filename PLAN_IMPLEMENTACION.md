# Plan de Implementación

## Objetivo
Realizar una CLI en Python para chatear con modelos LLM (Ollama, OpenAI y Gemini), incluyendo historial, streaming y robustez.

## Fases

### Fase 1 – Diseño y Alcances
1. Requisitos funcionales
   - Selección de proveedor y modelo.
   - Historial de conversación.
   - Streaming de tokens.
2. Requisitos no funcionales
   - CLI interactiva.
   - Manejo de errores.
   - Modularidad.

### Fase 2 – Preparar Entorno
- [x] Configurar layout de carpetas y archivos base.
- [x] Crear `requirements.txt` con dependencias iniciales.
- [x] Crear esqueleto de módulos: `cli.py`, `history.py`, y `providers/`.
- [ ] Instalar dependencias: `typer`, `openai`, `ollama-python`, `google-ai`.

### Fase 3 – Abstracción de Proveedores
- [x] Crear clase base para proveedores.
- [x] Implementar clase inicial `GeminiProvider` (simulación de respuesta).
- [x] Implementar adaptadores reales en `providers/openai.py` y `providers/ollama.py`.

### Fase 4 – CLI y Flujo Principal
- [x] CLI con `typer`.
- [x] Comando `chat --provider --model`.
- [x] Loop de entrada/salida con integración de proveedores.
- [x] Soporte para streaming de tokens (si API lo permite).

### Fase 5 – Historial y Persistencia
- [x] `history.py` para almacenar/recuperar JSON y agregar mensajes.
- [x] Opciones limpiar/exportar historial.

### Fase 6 – Gestión de Errores y Robustez
- [x] Captura de excepciones y reintentos con backoff en CLI.
- [x] Mensajes claros al usuario.

### Fase 7 – Pruebas y Documentación
- [x] Tests unitarios de adaptadores y módulo de historial (todos los tests pasaron exitosamente).
- [ ] Documentación de instalación y uso.

### Fase 8 – Empaquetado y Distribución
- `setup.py` o `pyproject.toml`.
- Entry point `chat-cli`.

### Fase 9 – Layout
```
chat_cli/
├── chat_cli/       # código fuente
│   ├── __main__.py
│   ├── cli.py
│   ├── providers/
│   │   ├── openai.py
│   │   ├── gemini.py
│   │   └── ollama.py
│   └── history.py
└── requirements.txt
```

### Fase 10 – Interfaz de Usuario en Terminal (TUI)
- [ ] Diseñar layout TUI con Textual (Header, ScrollView, Input, Footer)
- [ ] Crear `chat_cli/tui.py` e integrar comando `tui` en `cli.py`
- [ ] Gestionar streaming de tokens en la TUI
- [ ] Agregar dependencia `textual` a `requirements.txt`
- [ ] Documentar la TUI en README y en `PLAN_IMPLEMENTACION.md`