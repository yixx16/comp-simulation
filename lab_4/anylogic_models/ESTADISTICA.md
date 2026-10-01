# Estadística de los modelos AnyLogic

Datos obtenidos en el experimento nativo `Estadistica` de cada modelo. Python solo analiza los CSV exportados.

20 réplicas independientes por modelo, semillas 160005011–160005030 y estado inicial vacío. Job Shop: 8 horas; baterías: 4 horas. AnyLogic PLE limita Material Handling a 5 horas. Se mantienen las tasas y tiempos de la guía. El curado de baterías dura 2 minutos, como en el tutorial; no representa el tiempo industrial de 12–24 horas.

El IC de la media es media ± t(0.975,19) × desviación muestral / √20. Las réplicas, y no los agentes individuales, son la unidad estadística.

| Modelo | Medida | Media | Desv. estándar | IC 95% |
|---|---|---:|---:|---:|
| Job Shop | Producción conforme (unidades/horizonte) | 445.250 | 4.363 | [443.208, 447.292] |
| Job Shop | Producción conforme (unidades/h) | 55.656 | 0.545 | [55.401, 55.912] |
| Job Shop | Ciclo de salidas (min) | 57.124 | 2.261 | [56.066, 58.183] |
| Job Shop | WIP medio (unidades) | 57.312 | 2.126 | [56.317, 58.307] |
| Job Shop | WIP final (unidades) | 34.750 | 4.363 | [32.708, 36.792] |
| Job Shop | Utilización del recurso (%) | 95.829 | 0.171 | [95.749, 95.909] |
| Lead Acid Battery Production | Producción conforme (unidades/horizonte) | 33.400 | 4.706 | [31.197, 35.603] |
| Lead Acid Battery Production | Producción conforme (unidades/h) | 8.350 | 1.177 | [7.799, 8.901] |
| Lead Acid Battery Production | Ciclo de salidas (min) | 21.119 | 8.155 | [17.303, 24.936] |
| Lead Acid Battery Production | WIP medio (unidades) | 3.283 | 1.731 | [2.473, 4.093] |
| Lead Acid Battery Production | WIP final (unidades) | 3.600 | 2.927 | [2.230, 4.970] |
| Lead Acid Battery Production | Utilización del recurso (%) | 92.841 | 2.950 | [91.461, 94.222] |

En baterías se observaron 3 rechazos entre 671 salidas (0.447 %). El intervalo de Wilson 95 % del porcentaje agrupado es [0.152, 1.306] %. Este intervalo usa el supuesto binomial por unidad y no es el IC t de medias entre réplicas. Con tan pocos rechazos no permite una validación precisa del 1 % configurado.

El tiempo de ciclo incluye la espera desde la salida de Source hasta Sink. En baterías se mide desde la admisión de la caja. Se promedian únicamente los agentes que salen antes del horizonte de su modelo; los pendientes no se cuentan como terminados. WIP medio es la integral temporal exacta del número admitido aún presente, dividida por el horizonte.

La utilización corresponde al conjunto de dos CNC en Job Shop y al operador de ensamblaje en baterías. Es la utilización registrada por ResourcePool: incluye el tiempo durante el cual el recurso está reservado, y no solo el tiempo de procesamiento. En Job Shop el CNC se reserva antes de recuperar el pallet del rack. El rendimiento conforme excluye los rechazos. Son resultados transitorios desde vacío, sin calentamiento; no son estimaciones de régimen estacionario. Los horizontes distintos impiden una comparación directa entre ambos procesos.

Se verificó en todas las réplicas: entradas = salidas + WIP final y salidas = conformes + rechazadas. Las 40 corridas alcanzaron el horizonte completo y usaron 20 semillas diferentes por modelo.

Job Shop recibe 480 pallets por jornada y termina en promedio 445.25: quedan 34.75 pendientes. La alta utilización de CNC debe interpretarse con su política de reserva durante el transporte. Baterías entrega en promedio 33.4 unidades conformes en cuatro horas, frente a una llegada nominal de 40 cajas. La variación entre réplicas es mayor en baterías, especialmente en el tiempo de ciclo; el IC de la producción por hora tiene semiancho de 0.551 unidades/h, frente a 0.255 en Job Shop.

![Réplicas e intervalos](../imagenes/anylogic/estadistica_ic95.png)
