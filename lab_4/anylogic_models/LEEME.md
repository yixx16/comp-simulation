# Modelos propios del laboratorio 4

Se construyeron Job Shop y Lead Acid Battery Production desde un proyecto vacío creado en AnyLogic. Se conservaron el modelo Bank Office del estudiante y los demás archivos existentes. Subway Entrance e Intersection quedaron fuera del alcance solicitado.

## Abrir y ejecutar

- `Job Shop Lab4/Job Shop Lab4.alp`: modelo final con almacén, cinco montacargas, camiones y dos CNC.
- `Lead Acid Battery Lab4/Lead Acid Battery Lab4.alp`: modelo final con ocho etapas, dos líneas de electrodos, dos montacargas, operador, grúas, control de calidad y AGV.
- En cada modelo, ejecutar `Simulation` para ver el proceso. La presentación incluye indicadores y una ventana 3D debajo del diagrama; se puede acceder desplazando la vista.
- Ejecutar `Estadistica` para iniciar automáticamente 20 réplicas. Job Shop se detiene a los 480 minutos; baterías a los 14 400 segundos. El límite de Material Handling en PLE es cinco horas; por eso baterías usa cuatro horas.
- Los CSV se exportan a `C:/Users/jesus/projects/comp-simulation/lab_4/datos/anylogic/replicas`. Al mover el proyecto a otro equipo, ajustar ese destino en `Main → Advanced Java → Additional class code`.

Las carpetas `fases` conservan cinco etapas de Job Shop y ocho de baterías. Son hitos del desarrollo; la validación estadística corresponde a los archivos finales.

## Parámetros de la guía

Job Shop: cuatro racks, trece posiciones y dos niveles; almacenamiento `triangular(15,20,30)` minutos; cinco montacargas a 1 m/s; un camión por hora con 60 pallets; dos CNC con procesamiento de un minuto.

Baterías: lotes temporales de 100 electrodos; recubrimiento de un segundo; dos montacargas a 0.5 m/s; carga/descarga de horno de un minuto; curado de dos minutos; envoltura de un segundo; grupos de 15 ánodos y 15 cátodos; un operador y cinco minutos de ensamblaje; cajas a 10/h y cola de 25; grúas con carga/descarga de cinco segundos; tapa y terminales de un minuto; QA `uniform(20,30)` segundos con rechazo del 1 %; llenado de electrolito de dos minutos y capacidad tres; un AGV; rollos de 0.075 m³ cada dos horas; conversión de 0.0002 m³ por electrodo.

El curado de dos minutos es la simplificación didáctica del tutorial. No equivale al curado industrial de 12–24 horas. La disposición espacial es propia y se ajustó para evitar superposiciones de obstáculos y cubrir las posiciones de los buffers con las grúas. Los muros de presentación son visuales; no constituyen obstáculos adicionales.

## Procedencia y reproducción

La fuente es la ayuda oficial instalada con AnyLogic PLE 8.9.10: tutorial `job-shop` (fases 1–5) y `material-handling` (fases 1–8). Los textos de baterías están en `guias_oficiales`. Los recursos 3D son objetos estándar de la paleta instalada.

`build_from_scratch.py` y `build_battery.py` escriben las clases, conexiones y parámetros de los modelos propios. `library_schema.json` contiene identidades de componentes y nombres de parámetros para construir XML compatible. Los modelos resueltos en `referencias_preparadas` son referencias separadas: no son los modelos finales ni se importaron como base.

Para reconstruir, ejecutar en este orden: `build_from_scratch.py`, `build_battery.py`, `add_statistics.py`, `polish_models.py`. Abrir los modelos en AnyLogic y ejecutar sus experimentos `Estadistica`. Después ejecutar `analyze_statistics.py`: este script analiza únicamente los CSV producidos por AnyLogic y comprueba horizontes, semillas y balances; no sustituye el simulador.

Los resultados se describen en `ESTADISTICA.md`. Las capturas de ejecución y la gráfica están en `../imagenes/anylogic`.
