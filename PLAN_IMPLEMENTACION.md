# Plan de Implementación

**Historial de Cambios Recientes:**
*   2024-05-26: Implementada integración completa con API de Google Gemini. Añadida funcionalidad de listado de modelos OpenAI en la configuración TUI. Actualizada documentación.

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
- [x] Implementar clase `GeminiProvider` con integración real API.
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
- [x] Actualizada documentación de instalación y uso en README.md para reflejar el nuevo sistema de configuración `config.yaml`.

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
- [x] Documentadas mejoras del sistema de configuración en README.md y PLAN_IMPLEMENTACION.md.
- [ ] Documentar mejoras en README y `PLAN_IMPLEMENTACION.md`.

### Fase 10 – Integración con Model Context Protocol (M.C.P) de Anthropic
- [ ] Investigar la documentación oficial de M.C.P.
- [ ] Diseñar e implementar la integración de M.C.P como opción de proveedor/modelo.
- [ ] Añadir ejemplos de uso y documentación en el README.
- [ ] Garantizar modularidad y facilidad de mantenimiento en la integración.

## v0.2: actualizacion de 18-.5-25

A continuación, se enumeran las mejoras propuestas para futuras versiones del proyecto:

### Mejoras de Funcionalidad y Experiencia de Usuario (UX):

1.  **Gestión Avanzada de Contexto y Conversaciones:**
    *   Permitir guardar y cargar "sesiones" de chat completas.
    *   Ofrecer resumen de conversaciones largas por el LLM.
    *   Permitir edición de mensajes anteriores en la TUI y reenvío.
2.  **Soporte Mejorado para Model Context Protocol (MCP):**
    *   Mostrar herramientas MCP disponibles (si el modelo lo soporta).
    *   Interfaz para interactuar o pre-configurar herramientas MCP.
3.  **Configuración Más Flexible y Robusta:**
    *   [x] Implementar un archivo de configuración (ej. `config.yaml`) para API keys, modelos preferidos, etc.
        *   Se ha creado `config.yaml` en la raíz del proyecto para gestionar claves API y modelos por defecto.
        *   Se ha implementado `chat_cli/config.py` para cargar y gestionar la configuración desde `config.yaml`.
        *   Los módulos de proveedores (`openai.py`, `anthropic.py`, `gemini.py`, `ollama.py`) han sido actualizados para:
            *   Obtener claves API y modelos por defecto desde `config.py`.
            *   Seguir una jerarquía de prioridad: parámetros directos -> `config.yaml` -> variables de entorno -> valores por defecto internos.
        *   `cli.py` ha sido modificado para inicializar los proveedores utilizando este nuevo sistema de configuración, asegurando que los modelos por defecto se resuelvan correctamente.
        *   `config.yaml` ha sido añadido a `.gitignore` para proteger información sensible.
    *   [ ] Permitir perfiles de configuración (ej. "trabajo", "personal").
4.  **Integración Completa de Gemini:**
    *   [x] Finalizar la integración con la API real de Google Gemini.
5.  **Interfaz TUI Mejorada:**
    *   [x] Obtener y listar modelos disponibles desde la API del proveedor (si es posible) - Implementado para Ollama (local) y OpenAI (modelos GPT).
    *   Mejorar indicadores visuales (MCP, streaming).
    *   Opciones de personalización de la TUI (colores, disposición).
6.  **Manejo de Errores y Feedback Mejorado:**
    *   Mostrar mensajes de error más detallados en la TUI.
    *   Permitir configurar políticas de reintento para llamadas API.

### Mejoras Técnicas y de Desarrollo:

7.  **Sistema de Plugins/Extensiones para Proveedores:**
    *   Formalizar la adición de proveedores como un sistema de plugins dinámicos.
8.  **Pruebas Más Exhaustivas:**
    *   Añadir pruebas de integración (con mocks) para los adaptadores de proveedores.
    *   Explorar herramientas para pruebas de la TUI.
9.  **Documentación Avanzada:**
    *   Crear documentación para desarrolladores (cómo añadir proveedores, etc.).
    *   Incluir casos de uso y ejemplos avanzados en `README.md` o documentación separada.
10. **Empaquetado y Distribución Mejorados:**
    *   Empaquetar para instalación vía `pip install chat-llm-cli` (publicar en PyPI).
    *   Considerar distribución mediante `pipx`.

### Características Innovadoras:

11. **Comandos Personalizados dentro del Chat:**
    *   Permitir definir alias o comandos que la CLI interprete antes de enviar al LLM.
12. **Integración con Herramientas Locales:**
    *   Explorar la extensión de MCP para permitir a los LLM interactuar con herramientas o scripts locales definidos por el usuario.

---
creado por N.A.V.