# Irradiance Sensor para Home Assistant

Este componente personalizado permite integrar sensores de irradiancia, temperatura y viento en Home Assistant a través de Modbus TCP o RS485 (Serial). Diseñado para ser flexible, permite configurar modelos predefinidos o mapear registros personalizados paso a paso.

## ✨ Características

*   **Soporte Dual**: Conexión vía Modbus TCP (IP) o Modbus RTU (RS485/Serial).
*   **Múltiples Sensores**: Lectura de:
    *   Irradiancia (W/m²)
    *   Temperatura Externa e Interna (°C)
    *   Velocidad del Viento (m/s)
    *   Dirección del Viento (°)
*   **Configuración Guiada**: Asistente de configuración paso a paso para definir direcciones, ganancias y offsets.
*   **Plantillas**: Guarda tus configuraciones como plantillas para reutilizarlas en el futuro.
*   **Gestión de Errores**: Validaciones de conexión y parámetros.

## 🚀 Instalación

### Opción 1: Vía HACS (Recomendado)

1.  Asegúrate de tener [HACS](https://hacs.xyz/) instalado.
2.  Ve a **HACS** > **Integraciones**.
3.  Menú (tres puntos arriba a la derecha) > **Repositorios personalizados**.
4.  Añade la URL del repositorio: `https://github.com/Carlosjcfr/ha-irradiance-sensor`.
5.  Categoría: **Integración**.
6.  Pulsa **Añadir** y luego busca "Irradiance Sensor" para instalarlo.
7.  **Reinicia Home Assistant**.

### Opción 2: Manual

1.  Descarga el código fuente.
2.  Copia la carpeta `custom_components/irradiance_sensor` en tu directorio `config/custom_components/`.
3.  Reinicia Home Assistant.

## ⚙️ Configuración

Una vez instalado y reiniciado:

1.  Ve a **Ajustes** > **Dispositivos y servicios**.
2.  Pulsa **Añadir integración** y busca **Irradiance Sensor**.
3.  **Paso 1: Conexión**
    *   Selecciona **Modbus TCP** o **RS485**.
    *   Introduce los datos de conexión (IP/Puerto o Puerto Serie/Baudrate).
    *   Selecciona un **Modelo de Sensor** (o usa el Generico/Personalizado).
4.  **Paso 2: Mapeo de Parámetros**
    *   El asistente te guiará parámetro por parámetro (Irradiancia, Temperaturas, etc.).
    *   Para cada uno puedes definir:
        *   **Nombre**: Alias amigable.
        *   **Dirección (Addr)**: Registro Modbus.
        *   **Ganancia (Gain)**: Multiplicador (ej. 0.1 para convertir 123 en 12.3).
        *   **Offset**: Valor a sumar/restar.
5.  **Paso 3: Finalizar**
    *   Define el nombre de la entidad en Home Assistant.
    *   (Opcional) Guarda la configuración actual como una nueva plantilla.

## 🛠️ Solución de Problemas

*   **Error de conexión**: Verifica que la IP/Puerto sean correctos y que el dispositivo Modbus esté accesible.
*   **Lecturas erróneas**: Revisa la *Ganancia* y el *Offset* en la configuración. Muchos sensores envían valores enteros que requieren un factor de escala (ej. Gain 0.1).

## Créditos

Desarrollado para facilitar la integración de estaciones meteorológicas y piranómetros solares en Home Assistant.
