"""Notebook de análisis y paquete de entrega con recursos locales y datos reales."""
from pathlib import Path
import json,hashlib,zipfile
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
def md(s):return dict(cell_type='markdown',metadata={},source=s.splitlines(True))
def code(s):return dict(cell_type='code',execution_count=None,metadata={},outputs=[],source=s.splitlines(True))
cells=[md('''# AnyLogic: Job Shop y Lead Acid Battery Production

Modelos propios siguiendo las guías oficiales. Las simulaciones se ejecutaron en AnyLogic PLE 8.9.10; este notebook analiza sus CSV. Se conserva el trabajo previo de Bank Office y se excluyen los tutoriales 2 y 3.

20 réplicas por modelo; semillas 160005011–160005030. Job Shop: 8 horas. Baterías: 4 horas, dentro del límite de 5 horas de Material Handling en PLE. Estado inicial vacío; sin calentamiento. Los IC son para las medias transitorias entre réplicas.
'''),code('''from pathlib import Path
import pandas as pd
from IPython.display import display, Markdown, Image
root = Path.cwd()
if not (root / 'datos' / 'anylogic').exists():
    root = root / 'lab_4'
data = root / 'datos' / 'anylogic'
replicas = pd.read_csv(data / 'todas_las_replicas.csv')
resumen = pd.read_csv(data / 'resumen_ic95.csv')
display(resumen)
'''),code('''for model, df in replicas.groupby('model'):
    assert len(df) == 20 and df.seed.is_unique
    assert (df.entered == df.completed + df.wip).all()
    assert (df.completed == df.good + df.defective).all()
    expected = 14400 if model == 'battery' else 480
    assert (df.horizon == expected).all()
    print(model, ': 20 réplicas; horizonte y balances correctos')
'''),code('''display(Image(filename=str(root / 'imagenes' / 'anylogic' / 'estadistica_ic95.png')))
display(Markdown((root / 'anylogic_models' / 'ESTADISTICA.md').read_text(encoding='utf8')))
'''),md('''El ciclo de baterías comienza con la admisión de la caja, no con la preparación del electrodo. Solo se incluyen ciclos de agentes terminados; los restantes se registran como WIP. La utilización de recursos incluye tiempo reservado. Los horizontes diferentes impiden una comparación directa de los dos procesos.

Para recalcular a partir de los CSV individuales, ejecutar `anylogic_models/analyze_statistics.py`. Para generar nuevas réplicas, abrir cada `.alp` en AnyLogic y ejecutar `Estadistica`. No se ejecuta un sustituto del modelo en Python.
''')]
nb=dict(cells=cells,metadata=dict(kernelspec=dict(display_name='Python 3',language='python',name='python3'),language_info=dict(name='python',version='3.12')),nbformat=4,nbformat_minor=5)
(ROOT/'AnyLogic_estadistica.ipynb').write_text(json.dumps(nb,ensure_ascii=False,indent=2),encoding='utf8')
models=[ROOT/'anylogic_models'/'Job Shop Lab4'/'Job Shop Lab4.alp',ROOT/'anylogic_models'/'Lead Acid Battery Lab4'/'Lead Acid Battery Lab4.alp']
manifest=dict(anylogic_version='PLE 8.9.10',models=[dict(file=str(p.relative_to(ROOT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in models],replicas_per_model=20,seeds=[160005011,160005030],job_shop_hours=8,battery_hours=4,checks=['40 horizontes completos','entradas = salidas + WIP final','salidas = conformes + rechazadas'],latex_status='Fuente actualizada; compilador integrado no disponible: Unable to find standard directories for platform')
(ROOT/'datos'/'anylogic'/'validacion.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8')
files=[]
for folder in ['anylogic_models/Job Shop Lab4','anylogic_models/Lead Acid Battery Lab4','datos/anylogic','imagenes/anylogic']:
    files.extend(p for p in (ROOT/folder).rglob('*') if p.is_file() and p.suffix not in ['.bak','.log'])
files.extend(ROOT/'anylogic_models'/n for n in ['LEEME.md','ESTADISTICA.md','build_from_scratch.py','build_battery.py','add_statistics.py','polish_models.py','analyze_statistics.py','package_results.py','library_schema.json','experimento_creado_en_app.xml'])
files.extend(p for p in (ROOT/'anylogic_models'/'guias_oficiales').glob('*.txt'))
files.append(ROOT/'AnyLogic_estadistica.ipynb')
dest=ROOT/'Lab4_AnyLogic_entrega.zip'
with zipfile.ZipFile(dest,'w',compression=zipfile.ZIP_DEFLATED) as z:
    for p in files:z.write(p,'lab_4/'+p.relative_to(ROOT).as_posix())
print(dest,round(dest.stat().st_size/1024/1024,2),'MB',len(files),'archivos')
