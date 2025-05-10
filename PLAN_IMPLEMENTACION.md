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

### Fase 9 – Layout, Markdown y Performance en la TUI
- [x] Agregar dependencia `textual` a `requirements.txt` y crear `chat_cli/tui.py`.
- [x] Integrar comando `tui` en `cli.py`.
- [x] Estilizar TUI con Rich usando `Panel`, `Align` y `Markdown`.
- [x] Renderizar respuestas en Markdown en la TUI.
- [x] Optimizar streaming: agrupar tokens (batch <5 tokens o 200ms) antes de actualizar panel.
- [x] Reducir renders usando `widget.update` y atributos reactivos en lugar de remount completo.
- [x] Lazy import de `rich.markdown.Markdown` para mejorar tiempo de inicio.
- [x] Usar atributos reactivos (`reactive`) para `status_text`, `history`, `token_count` y `tokens_per_second`.
- [ ] Documentar mejoras en README y `PLAN_IMPLEMENTACION.md`.

### Fase 10 – Integración con Model Context Protocol (M.C.P) de Anthropic
- [ ] Investigar la documentación oficial de M.C.P.
- [ ] Diseñar e implementar la integración de M.C.P como opción de proveedor/modelo.
- [ ] Añadir ejemplos de uso y documentación en el README.
- [ ] Garantizar modularidad y facilidad de mantenimiento en la integración.