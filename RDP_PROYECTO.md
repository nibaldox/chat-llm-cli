# Registro Detallado del Proyecto (RDP)

## 1. Propósito
Establecer un documento vivo para seguimiento del desarrollo de la CLI en Python que integre LLMs (Ollama, OpenAI, Gemini).

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
| **Release v1.0**      | Entrega funcional inicial                | 2025-05-20      |

## 5. Entregables
- `PLAN_IMPLEMENTACION.md`
- `RDP_PROYECTO.md`
- Código fuente en `chat_cli/`
- Tests en `tests/`

## 6. Riesgos y Mitigaciones
- **Dependencia de APIs externas**: controlar límites de tasa y excepciones.
- **Cambios en esquemas de API**: versionar adaptadores.
- **Latencia de red**: implementar timeouts y feedback al usuario.

## 7. Control de Cambios
- **v1.0** (2025-05-20): Plan inicial y versión mínima viable.
- Futuras versiones documentarán nuevas características.
