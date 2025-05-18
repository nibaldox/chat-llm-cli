# Registro Detallado del Proyecto (RDP)

## 1. Propósito
Establecer un documento vivo para seguimiento del desarrollo de la CLI en Python que integre LLMs (Ollama, OpenAI, Gemini, Anthropic).

## 2. Alcance
- Desarrollo de CLI interactiva.
- Módulos de proveedor de LLM.
- Historial y streaming de tokens.
- Pruebas y empaquetado.

## 3. Roles y Responsabilidades
- **Product Owner**: Definir requisitos y validar entregables.
- **Desarrollador**: Implementar funcionalidades según plan.
- **Tester**: Crear y ejecutar casos de prueba.

## 4. Cronograma y Hitos
| Hito                  | Descripción                              | Fecha Objetivo  |
|-----------------------|------------------------------------------|-----------------|
| Fase 1 – Diseño       | Requisitos y alcance                     | 2025-05-03      |
| Fase 2 – Entorno      | Configuración y dependencias             | 2025-05-05      |
| Fase 3 – Proveedores  | Implementar adaptadores de API           | 2025-05-07      |
| Fase 4 – CLI          | CLI principal y streaming                | 2025-05-10      |
| Fase 5 – Historial    | Módulo de persistencia                   | 2025-05-12      |
| Fase 6 – Errores      | Manejo de excepciones y reintentos       | 2025-05-14      |
| Fase 7 – Pruebas      | Unit tests y QA                          | 2025-05-16      |
| Fase 8 – Empaquetado  | Empaquetado y distribución               | 2025-05-18      |
| **Release v1.0**      | Entrega funcional inicial con TUI y soporte MCP (Anthropic) | 2025-05-20      |

## 5. Entregables
- `PLAN_IMPLEMENTACION.md`
- `RDP_PROYECTO.md`
- Código fuente en `chat_cli/`
  - Incluye `chat_cli/config.py` para la gestión de configuración.
- `config.yaml` (archivo de configuración del usuario, en `.gitignore`)
- Tests en `tests/`

## 6. Riesgos y Mitigaciones
- **Dependencia de APIs externas**: controlar límites de tasa y excepciones.
- **Cambios en esquemas de API**: versionar adaptadores.
- **Latencia de red**: implementar timeouts y feedback al usuario.

## 7. Control de Cambios
- **v1.0** (2025-05-20): Versión funcional inicial con interfaz TUI, soporte para proveedores Ollama, OpenAI, Gemini y Anthropic, gestión de historial, y M.C.P experimental para Anthropic.
- Futuras versiones documentarán nuevas características.

## 8. Decisiones de Diseño Clave

- **2025-05-18: Implementación de Sistema de Configuración Centralizado (`config.yaml`)**
  - **Decisión**: Implementar un sistema de configuración basado en un archivo `config.yaml` para gestionar claves API, modelos por defecto y otras configuraciones de proveedores.
  - **Justificación**:
    - Centralizar la configuración mejora la organización y facilita la gestión de múltiples proveedores y sus credenciales.
    - Evita la necesidad de usar exclusivamente variables de entorno para todas las configuraciones, lo que puede ser engorroso.
    - Proporciona una jerarquía clara para la obtención de configuraciones (parámetros de CLI > `config.yaml` > variables de entorno > defaults internos).
    - Mejora la seguridad al permitir que `config.yaml` (que contiene claves API) sea incluido en `.gitignore` fácilmente.
  - **Implicaciones**:
    - Creación del módulo `chat_cli/config.py` para cargar y parsear `config.yaml`.
    - Modificación de las clases de proveedores para utilizar `config.py`.
    - Actualización de `cli.py` para pasar la configuración adecuada.
    - Actualización de `README.md`, `PLAN_IMPLEMENTACION.md` y `RDP_PROYECTO.md`.

---
creado por N.A.V.
