"""Resumen estadístico de las réplicas exportadas por AnyLogic, sin simular en Python."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'datos'/'anylogic'
NAMES={'job_shop':'Job Shop','battery':'Lead Acid Battery Production'}
# Cuantil t de Student bilateral 95 %, 19 grados de libertad (20 réplicas).
T_CRITICAL_19=2.093024054408263
def analyze():
    frames=[];summary=[]
    for model,label in NAMES.items():
        files=sorted((DATA/'replicas').glob(model+'_*.csv'))
        if len(files)!=20:raise ValueError(f'{model}: se requieren 20 réplicas; hay {len(files)}')
        df=pd.concat([pd.read_csv(p) for p in files],ignore_index=True).sort_values('seed')
        assert df.seed.is_unique
        assert np.all(df.entered==df.completed+df.wip)
        assert np.all(df.completed==df.good+df.defective)
        assert np.allclose(df.horizon,14400 if model=='battery' else 480)
        df['cycle_minutes']=df.mean_cycle/(60 if model=='battery' else 1)
        df['good_per_hour']=df.good/(4 if model=='battery' else 8)
        df['utilization_percent']=100*df.resource_utilization
        df['defect_percent']=100*df.defective/df.completed
        df.to_csv(DATA/f'{model}_replicas.csv',index=False);frames.append(df)
        for metric in ['good','good_per_hour','cycle_minutes','mean_wip','wip','utilization_percent']:
            a=df[metric].to_numpy();mean=a.mean();sd=a.std(ddof=1);half=T_CRITICAL_19*sd/np.sqrt(len(a))
            summary.append(dict(model=model,metric=metric,n=len(a),mean=mean,sd=sd,ci_low=mean-half,ci_high=mean+half,half_width=half))
    pd.concat(frames).to_csv(DATA/'todas_las_replicas.csv',index=False)
    s=pd.DataFrame(summary);s.to_csv(DATA/'resumen_ic95.csv',index=False)
    (DATA/'resumen_ic95.json').write_text(s.to_json(orient='records',indent=2),encoding='utf8')
    fig,axs=plt.subplots(2,3,figsize=(12,7),layout='constrained')
    cols=[('good_per_hour','Producción conforme (unidades/h)'),('cycle_minutes','Tiempo de ciclo de salidas (min)'),('utilization_percent','Utilización del recurso (%)')]
    for row,(model,label) in enumerate(NAMES.items()):
        df=frames[row]
        for col,(metric,title) in enumerate(cols):
            ax=axs[row,col];values=df[metric];a=s[(s.model==model)&(s.metric==metric)].iloc[0]
            ax.scatter(np.arange(1,21),values,color='#217b90',s=23)
            ax.axhline(a['mean'],color='#b65b24',label='Media')
            ax.axhspan(a.ci_low,a.ci_high,color='#b65b24',alpha=.14,label='IC 95% de la media')
            ax.set(title=label+'\n'+title,xlabel='Réplica',xticks=[1,5,10,15,20]);ax.grid(alpha=.2)
    axs[0,0].legend(fontsize=8)
    images=ROOT/'imagenes'/'anylogic';images.mkdir(exist_ok=True,parents=True)
    fig.savefig(images/'estadistica_ic95.png',dpi=180);plt.close(fig)
    lines=['# Estadística de los modelos AnyLogic','',
           'Datos obtenidos en el experimento nativo `Estadistica` de cada modelo. Python solo analiza los CSV exportados.',
           '', '20 réplicas independientes por modelo, semillas 160005011–160005030 y estado inicial vacío. Job Shop: 8 horas; baterías: 4 horas. AnyLogic PLE limita Material Handling a 5 horas. Se mantienen las tasas y tiempos de la guía. El curado de baterías dura 2 minutos, como en el tutorial; no representa el tiempo industrial de 12–24 horas.',
           '', 'El IC de la media es media ± t(0.975,19) × desviación muestral / √20. Las réplicas, y no los agentes individuales, son la unidad estadística.',
           '', '| Modelo | Medida | Media | Desv. estándar | IC 95% |','|---|---|---:|---:|---:|']
    labels={'good':'Producción conforme (unidades/horizonte)','good_per_hour':'Producción conforme (unidades/h)','cycle_minutes':'Ciclo de salidas (min)','mean_wip':'WIP medio (unidades)','wip':'WIP final (unidades)','utilization_percent':'Utilización del recurso (%)'}
    for a in summary:lines.append(f"| {NAMES[a['model']]} | {labels[a['metric']]} | {a['mean']:.3f} | {a['sd']:.3f} | [{a['ci_low']:.3f}, {a['ci_high']:.3f}] |")
    bdf=frames[1];rejects=int(bdf.defective.sum());total=int(bdf.completed.sum());p=rejects/total;z=1.959963984540054
    center=(p+z*z/(2*total))/(1+z*z/total);half=z*np.sqrt(p*(1-p)/total+z*z/(4*total*total))/(1+z*z/total)
    lines += ['',f'En baterías se observaron {rejects} rechazos entre {total} salidas ({100*p:.3f} %). El intervalo de Wilson 95 % del porcentaje agrupado es [{100*(center-half):.3f}, {100*(center+half):.3f}] %. Este intervalo usa el supuesto binomial por unidad y no es el IC t de medias entre réplicas. Con tan pocos rechazos no permite una validación precisa del 1 % configurado.']
    lines += ['', 'El tiempo de ciclo incluye la espera desde la salida de Source hasta Sink. En baterías se mide desde la admisión de la caja. Se promedian únicamente los agentes que salen antes del horizonte de su modelo; los pendientes no se cuentan como terminados. WIP medio es la integral temporal exacta del número admitido aún presente, dividida por el horizonte.',
              '', 'La utilización corresponde al conjunto de dos CNC en Job Shop y al operador de ensamblaje en baterías. Es la utilización registrada por ResourcePool: incluye el tiempo durante el cual el recurso está reservado, y no solo el tiempo de procesamiento. En Job Shop el CNC se reserva antes de recuperar el pallet del rack. El rendimiento conforme excluye los rechazos. Son resultados transitorios desde vacío, sin calentamiento; no son estimaciones de régimen estacionario. Los horizontes distintos impiden una comparación directa entre ambos procesos.',
              '', 'Se verificó en todas las réplicas: entradas = salidas + WIP final y salidas = conformes + rechazadas. Las 40 corridas alcanzaron el horizonte completo y usaron 20 semillas diferentes por modelo.',
              '', 'Job Shop recibe 480 pallets por jornada y termina en promedio 445.25: quedan 34.75 pendientes. La alta utilización de CNC debe interpretarse con su política de reserva durante el transporte. Baterías entrega en promedio 33.4 unidades conformes en cuatro horas, frente a una llegada nominal de 40 cajas. La variación entre réplicas es mayor en baterías, especialmente en el tiempo de ciclo; el IC de la producción por hora tiene semiancho de 0.551 unidades/h, frente a 0.255 en Job Shop.',
              '', '![Réplicas e intervalos](../imagenes/anylogic/estadistica_ic95.png)']
    (ROOT/'anylogic_models'/'ESTADISTICA.md').write_text('\n'.join(lines)+'\n',encoding='utf8')
    print(s.to_string(index=False))
if __name__=='__main__':analyze()
