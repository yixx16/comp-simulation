"""Prepara copias atribuidas de los tutoriales oficiales instalados con AnyLogic."""
from pathlib import Path
import shutil
import re
import json
import hashlib
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent
SOURCE = Path('C:/ProgramData/AnyLogic 8.9 Personal Learning Edition/eclipse/plugins/com.anylogic.examples_8.9.10.202609231424/basicmodels')
SPECS = [
    ('Subway Entrance', 'Subway Entrance Hall - Phase ', 4, 60, 'Minute', 'pedestrian'),
    ('Intersection', 'Road Traffic Tutorial - Phase ', 6, 3600, 'Second', 'road-traffic'),
    ('Job Shop', 'Job Shop - Phase ', 5, 480, 'Minute', 'job-shop'),
    ('Lead Acid Battery Production', 'Lead Acid Battery Production Phase ', 8, 28800, 'Second', 'material-handling'),
]

def replace_tag(text, tag, value):
    result, count = re.subn(rf'(<{tag}>).*?(</{tag}>)', lambda m: m[1] + value + m[2], text, flags=re.S)
    if count != 1:
        raise ValueError(f'{tag}: expected one occurrence, got {count}')
    return result

manifest = []
for name, prefix, phases, horizon, unit, guide in SPECS:
    dest = ROOT / name
    if (dest / (name + '.alp')).exists():
        raise FileExistsError(f'El modelo ya existe: {dest}')
    for phase in range(1, phases + 1):
        official = prefix + str(phase)
        shutil.copytree(SOURCE / official, dest / 'fases_oficiales' / f'fase_{phase:02d}')
    original = SOURCE / (prefix + str(phases))
    dest.mkdir(parents=True, exist_ok=True)
    for resource in original.iterdir():
        if resource.suffix.lower() == '.alp':
            continue
        if resource.is_dir():
            shutil.copytree(resource, dest / resource.name)
        else:
            shutil.copy2(resource, dest / resource.name)
    source_file = original / (prefix + str(phases) + '.alp')
    text = source_file.read_text(encoding='utf-8')
    # Cambia solamente el nombre del modelo y la configuración del experimento.
    text = re.sub(r'(<Model>\s*<Id>.*?</Id>\s*<Name>).*?(</Name>)', lambda m: m[1] + '<![CDATA[' + name + ' - Lab4]]>' + m[2], text, count=1, flags=re.S)
    match = re.search(r'<SimulationExperiment\b.*?</SimulationExperiment>', text, re.S)
    exp = match[0]
    for tag, value in [('Title', '<![CDATA[' + name + ' - Lab4 : Simulation]]>'),
                       ('RandomNumberGenerationType', 'fixedSeed'), ('SeedValue', '1'),
                       ('StopOption', '<![CDATA[Stop at specified time]]>'),
                       ('InitialTime', '0.0'), ('FinalTime', str(horizon)),
                       ('ExecutionMode', '<![CDATA[fast]]>'), ('BypassInitialScreen', 'true')]:
        exp = replace_tag(exp, tag, value)
    text = text[:match.start()] + exp + text[match.end():]
    target = dest / (name + '.alp')
    target.write_text(text, encoding='utf-8')
    tree = ET.fromstring(text)
    assert tree.findtext('Model/ModelTimeUnit') == unit
    resources = [e.text for e in tree.findall('Model/ModelResources/Resource/Path')]
    missing = [r for r in resources if not (dest / r).exists()]
    if missing:
        raise FileNotFoundError(missing)
    manifest.append(dict(model=name, file=str(target.relative_to(ROOT)), official_source=str(source_file),
                         official_sha256=hashlib.sha256(source_file.read_bytes()).hexdigest(),
                         phases=phases, seed=1, horizon=horizon, time_unit=unit,
                         guide=f'https://anylogic.help/tutorials/{guide}/index.html',
                         validation='Pendiente de ejecutar en AnyLogic'))
    (dest / 'ORIGEN.md').write_text(
        f'# {name}\n\nBase: modelo oficial de The AnyLogic Company, fase {phases}. '
        f'Guía: https://anylogic.help/tutorials/{guide}/index.html\n\n'
        'Las carpetas `fases_oficiales` contienen copias sin modificaciones de las referencias '
        'instaladas con AnyLogic 8.9.10. No fueron construidas desde cero por el estudiante.\n\n'
        f'La copia final conserva la lógica y los recursos oficiales. Cambios para Lab4: '
        f'nombre y título propios, semilla fija 1, inicio en 0, parada en {horizon} '
        f'{unit}, ejecución en tiempo virtual y apertura directa de la animación. '
        'El horizonte es una elección para la prueba, no un requisito numérico del PDF.\n', encoding='utf-8')
(ROOT / 'modelos_manifest.json').write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding='utf-8')
print(json.dumps(manifest, indent=2, ensure_ascii=False))
