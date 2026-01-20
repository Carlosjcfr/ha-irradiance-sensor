# Análisis de Calidad de Integración (Home Assistant Quality Scale)

Este documento detalla las razones por las cuales la integración `irradiance_sensor` no cumple actualmente con el nivel **Oro** (Gold) de la escala de calidad de Home Assistant.

Referencia: [Integration Quality Scale](https://developers.home-assistant.io/docs/core/integration-quality-scale/rules)

## 🛑 Bloqueantes para Nivel Plata (Silver)
El nivel Plata es un prerrequisito para Oro.

1.  **Test Coverage (Cobertura de Pruebas)**
    *   **Estado**: ❌ Inexistente.
    *   **Requisito**: Más del 95% de cobertura en todos los módulos, incluyendo pruebas completas para el flujo de configuración (`config_flow`). No existe carpeta `tests/`.

2.  **Code Owner (Propietario del Código)**
    *   **Estado**: ❌ Vacío.
    *   **Requisito**: El archivo `manifest.json` debe tener al menos un usuario de GitHub válido en `codeowners`.

3.  **Entity Naming (Nombrado de Entidades)**
    *   **Estado**: ⚠️ Implementación manual.
    *   **Requisito**: Las entidades deben definir `_attr_has_entity_name = True` y confiar en el nombre del dispositivo para la primera parte de su nombre, usando `translation_key` o `name` (solo el sufijo). Actualmente se construye el nombre completo manualmente.

## 🏆 Bloqueantes para Nivel Oro (Gold)

4.  **Reconfiguration Flow (Flujo de Reconfiguración)**
    *   **Estado**: ❌ No implementado.
    *   **Requisito**: Debe permitir al usuario cambiar parámetros (IP, Puerto, etc.) sin eliminar y volver a añadir la integración.

5.  **Diagnostics (Diagnósticos)**
    *   **Estado**: ❌ No implementado.
    *   **Requisito**: Debe existir un archivo `diagnostics.py` que permita descargar información de depuración censurada desde la interfaz de HA.

6.  **Documentation (Documentación Completa)**
    *   **Estado**: ⚠️ Parcial.
    *   **Requisito**: Falta secciones específicas en `README.md` (o archivo enlazado):
        *   **Ejemplos de Automatización**: Casos de uso reales.
        *   **Limitaciones Conocidas**: Qué no puede hacer.
        *   **Solución de Problemas**: Guía detallada.

7.  **Icon Translations (Traducción de Iconos)**
    *   **Estado**: ❌ No implementado.
    *   **Requisito**: Los iconos de las entidades deben poder definirse/traducirse en `strings.json` o `icons.json` dependiendo del estado, si aplica.

8.  **Strict Typing (Tipado Estricto)**
    *   **Estado**: ❓ No verificado.
    *   **Requisito**: El código debe pasar la validación `mypy` en modo estricto.

## Resumen de Acciones Recomendadas

1.  Crear carpeta `tests/` e implementar pruebas unitarias con `pytest`.
2.  Añadir tu usuario de GitHub en `manifest.json`.
3.  Refactorizar `IrradianceSensorEntity` para usar `has_entity_name = True`.
4.  Implementar `async_step_reconfigure` en `config_flow.py`.
5.  Crear `diagnostics.py`.
6.  Ampliar `README.md` con ejemplos y limitaciones.
