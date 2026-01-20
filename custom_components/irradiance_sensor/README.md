# Irradiance Sensor Custom Component

Este componente personalizado para Home Assistant permite integrar sensores de irradiancia mediante Modbus TCP o RS485. Permite mapear registros personalizados o utilizar plantillas predefinidas.

## Instalación

### Vía HACS (Repositorio Privado)

Como este es un repositorio privado, necesitas asegurarte de que tu instalación de HACS tiene acceso a él.

1.  Asegúrate de que HACS está instalado y funcionando.
2.  Ve a **HACS** > **Integraciones**.
3.  Haz clic en los 3 puntos en la esquina superior derecha y selecciona **Repositorios personalizados**.
4.  Pega la URL de este repositorio: `https://github.com/tu_usuario/HA-Solar_integrations` (Sustituye por tu URL real).
5.  En **Categoría**, selecciona **Integración**.
6.  Haz clic en **Añadir**.
7.  Ahora busca "Irradiance Sensor" en la lista de integraciones de HACS e instálalo.
8.  Reinicia Home Assistant.

### Instalación Manual

1.  Copia la carpeta `custom_components/irradiance_sensor` dentro de la carpeta `custom_components` de tu directorio de configuración de Home Assistant.
2.  Reinicia Home Assistant.

## Configuración

1.  Ve a **Ajustes** > **Dispositivos y servicios**.
2.  Haz clic en **Añadir integración**.
3.  Busca **Irradiance Sensor**.
4.  Sigue los pasos del configurador:
    *   **Paso 1**: Selecciona el método de conexión (TCP o RS485) y los parámetros correspondientes. Puedes elegir un modelo predefinido o "Custom".
    *   **Paso 2**: Ajusta las direcciones de los registros Modbus, ganancias y offsets si es necesario. Puedes guardar tu configuración como una nueva plantilla.

## Características

*   Soporte Modbus TCP y Serial (RS485).
*   Lectura de Irradiancia, Temperatura (Ext/Int), Viento (Vel/Dir).
*   Plantillas de configuración guardables.
*   Totalmente configurable desde la UI de Home Assistant.
