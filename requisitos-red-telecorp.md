# Red TeleCorp — Requisitos de la solución

La solución debe ayudar a Red TeleCorp a detectar fallas de telefonía e Internet, priorizar su atención y mantener informados a los usuarios afectados. El alcance cubre la ingesta de señales, el seguimiento de incidencias y el análisis histórico.

## Requisitos funcionales

| ID | Requisito | Criterio de aceptación |
| --- | --- | --- |
| RF-01 | Recibir datos de las antenas y los sistemas internos. | El sistema procesa métricas periódicas de tráfico por antena, en GB por minuto, y recibe registros operativos de los sistemas internos. |
| RF-02 | Clasificar el estado operativo de las antenas. | Con 0 GB/min la antena se clasifica como **inhabilitada**. Con tráfico mayor que 0 y menor que 60 GB/min, se clasifica como **caída**. De 60 a 129 GB/min, inclusive, se clasifica como **normal**. Por encima de 129 GB/min, se clasifica como **saturada**. |
| RF-03 | Registrar reportes de usuarios mediante una API. | La API acepta identificación del usuario, número asociado al servicio, ubicación aproximada, fecha y hora del problema, tipo y descripción. |
| RF-04 | Consultar y administrar el ciclo de vida de una incidencia. | Cada incidencia tiene un estado consultable — registrada, en revisión, en atención, solucionada o cerrada — y un historial de los cambios con su fecha y hora. |
| RF-05 | Detectar posibles incidencias colectivas por zona. | Al recibir reportes de problemas relacionados de al menos 10 usuarios distintos en la misma zona dentro de un intervalo menor de 24 horas, el sistema identifica un posible incidente colectivo e inicia la verificación de la infraestructura correspondiente. Los reportes repetidos de una persona cuentan una sola vez para el umbral. |
| RF-06 | Detectar fallas de forma proactiva y correlacionar señales. | El sistema puede alertar al equipo de operaciones a partir de la telemetría, incluso antes del primer reporte de usuario. Cuando existen reportes, los relaciona con los eventos de infraestructura de la zona y el período correspondiente. |
| RF-07 | Notificar a quienes reportaron una incidencia en la zona afectada. | Los usuarios reciben avisos por correo electrónico y/o celular cuando el problema está en evaluación, se confirma la afectación en la zona o se restablece el servicio. |
| RF-08 | Priorizar incidencias según el impacto. | El equipo puede distinguir una falla de alcance reducido de otra que afecta a muchos usuarios o a zonas con servicios críticos, como centros médicos. |
| RF-09 | Identificar patrones y fallas recurrentes. | Operaciones puede consultar qué zonas acumulan más incidencias, qué antenas fallan con mayor frecuencia y qué tipos de problemas se repiten. Una antena puede quedar identificada como recurrente aunque se recupere entre fallas. |
| RF-10 | Consultar la evolución histórica del servicio. | Se puede consultar cuánto duró cada incidencia, qué zonas afectó, cuántos usuarios estuvieron involucrados y con qué frecuencia falló la infraestructura. |

## Requisitos técnicos

| ID | Requisito | Criterio de aceptación |
| --- | --- | --- |
| RT-01 | Implementar una arquitectura completamente serverless en **AWS y Microsoft Azure**. | Ambas nubes cumplen una función dentro de un flujo de la solución. El diagrama identifica qué corre en cada nube y cómo se intercambian datos. La operación se apoya en servicios administrados, sin servidores propios encendidos permanentemente. |
| RT-02 | Orquestar automatizaciones con **AWS Step Functions**. | Existe al menos un flujo ejecutable ligado a un proceso del caso, como verificar una posible incidencia colectiva y notificar a los usuarios. La ejecución permite identificar el resultado y dónde ocurrió un error, si lo hubo. |
| RT-03 | Proteger los valores sensibles de las variables de configuración globales con un servicio de AWS. | Las contraseñas, claves y tokens se guardan en un servicio administrado, como **AWS Secrets Manager**, y solo los componentes autorizados pueden leerlos. El código, el repositorio y los logs quedan libres de estos valores. |
| RT-04 | Garantizar persistencia y alta disponibilidad de los datos. | Los reportes, estados e historiales se guardan en almacenamiento duradero y de alta disponibilidad. Los datos permanecen consultables tras reinicios o ejecuciones fallidas. DynamoDB es una opción para los reportes y las incidencias. |
| RT-05 | Procesar picos de métricas y reportes simultáneos. | Una prueba de ráfaga verifica que los eventos aceptados se procesan o quedan pendientes de procesamiento sin pérdida y que los reintentos no generan incidencias ni notificaciones duplicadas. |
| RT-06 | Incorporar IA a una función del sistema. | La demo muestra una entrada realista y su resultado dentro del flujo. Un caso de uso posible es clasificar o resumir reportes para facilitar la revisión por operaciones. |
| RT-07 | Diseñar para escalar con el volumen y controlar el costo operativo. | La arquitectura explica qué componentes escalan al aumentar los eventos y qué operaciones impulsan el costo, desde la ingesta hasta el almacenamiento y las notificaciones. |

**Supuesto de simulación.** Se incluyen los valores exactos 60 y 129 GB/min en el estado normal, ya que los umbrales de caída y saturación del enunciado usan desigualdades estrictas.

## Arquitectura y presentación

- Presentar un diagrama con los componentes de AWS y Azure, el flujo de datos, la orquestación, la persistencia, la gestión de secretos y el punto donde interviene la IA.
- Preparar un **pitch de 5 minutos** que explique el problema, muestre cómo funciona la solución y exponga el valor para Red TeleCorp.

## Rúbrica de evaluación

| Criterio | Puntaje máximo |
| --- | ---: |
| Cobertura de los problemas del caso | 3 |
| Persistencia y alta disponibilidad | 2 |
| Automatización con Step Functions | 2 |
| Uso de dos o más nubes | 3 |
| Arquitectura de la solución | 3 |
| Pitch de 5 minutos | 2 |
| Solución completamente serverless | 2 |
| Uso de IA en la solución | 3 |
| **Total** | **20** |
