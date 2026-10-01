"""Autoría de modelos ALP a partir del proyecto vacío creado en la app.

library_schema.json aporta exclusivamente identidades y nombres de parámetros
de los componentes de biblioteca; no contiene configuraciones de tutoriales.
"""
from pathlib import Path
import xml.etree.ElementTree as E
import copy
import json
import shutil

ROOT = Path(__file__).resolve().parent
SCHEMA = json.loads((ROOT / 'library_schema.json').read_text())
BASE = ROOT / 'Job Shop Lab4' / 'inicio_creado_en_app.alp'
seq = 1790794000000

def uid():
    global seq
    seq += 1
    return str(seq)

def child(parent, tag, text=None, **attrs):
    e = E.SubElement(parent, tag, attrs)
    if text is not None:
        e.text = str(text)
    return e

def settext(parent, tag, text):
    e = parent.find(tag)
    if e is None:
        e = child(parent, tag)
    e.text = str(text)
    return e

def common(tag, name, x=0, y=0, **attrs):
    e = E.Element(tag, attrs)
    for key, value in [('Id', uid()), ('Name', name), ('X', x), ('Y', y)]:
        child(e, key, value)
    label = child(e, 'Label')
    child(label, 'X', 0); child(label, 'Y', -20)
    for key, value in [('PublicFlag', 'true'), ('PresentationFlag', 'true'), ('ShowLabel', 'false')]:
        child(e, key, value)
    return e

def unit(code, dimension='TimeUnits', symbol='MINUTE'):
    return (str(code), dimension, symbol)

def entity(name):
    return {'entity': name}

def setparam(e, name, value, package='job_shop_lab4'):
    params = e.find('Parameters')
    if params is None:
        params = child(e, 'Parameters')
    p = next((p for p in params if p.findtext('Name') == name), None)
    if p is None:
        p = child(params, 'Parameter'); child(p, 'Name', name)
    for old in list(p):
        if old.tag != 'Name': p.remove(old)
    if isinstance(value, tuple):
        v = child(p, 'Value', Class='CodeUnitValue')
        child(v, 'Code', value[0]); child(v, 'Unit', value[2], Class=value[1])
    elif isinstance(value, dict):
        v = child(p, 'Value', Class='EntityCodeValue')
        child(v, 'IsAgentEntity', 'true')
        ob = child(v, 'EntityEmbeddedObject')
        ref = child(ob, 'ActiveObjectClass')
        child(ref, 'PackageName', package); child(ref, 'ClassName', value['entity'])
        child(ob, 'Parameters')
        child(ob, 'ReplicationFlag', 'false')
        child(child(ob, 'Replication', Class='CodeValue'), 'Code', 100)
        child(ob, 'CollectionType', 'ARRAY_LIST_BASED')
        child(ob, 'InitialLocationType', 'AT_ANIMATION_POSITION')
    else:
        v = child(p, 'Value', Class='CodeValue'); child(v, 'Code', value)

def descriptor(kind, name, x, y, params=None, package=None):
    key = next(k for k, v in SCHEMA.items() if v['class'] == kind and (package is None or v['package'] == package))
    meta = SCHEMA[key]
    e = common('EmbeddedObject', name, x, y)
    settext(e, 'ShowLabel', 'true')
    ref = child(e, 'ActiveObjectClass')
    child(ref, 'PackageName', meta['package']); child(ref, 'ClassName', kind)
    if meta['generic']:
        ref = child(child(e, 'GenericParameterSubstitute'), 'GenericParameterSubstituteReference')
        child(ref, 'PackageName', meta['package']); child(ref, 'ClassName', kind); child(ref, 'ItemName', meta['generic'])
    ps = child(e, 'Parameters')
    for p in meta['parameters']:
        child(child(ps, 'Parameter'), 'Name', p)
    for p, value in (params or {}).items(): setparam(e, p, value)
    child(e, 'ReplicationFlag', 'false')
    child(child(e, 'Replication', Class='CodeValue'), 'Code', 100)
    child(e, 'CollectionType', 'ARRAY_LIST_BASED')
    child(e, 'InitialLocationType', 'AT_ANIMATION_POSITION')
    return e

def block(c, kind, name, x, y, params=None):
    objects = c.find('EmbeddedObjects')
    if objects is None: objects = child(c, 'EmbeddedObjects')
    e = descriptor(kind, name, x, y, params)
    objects.append(e)
    return e

def connect(c, a, b, out='out', into='in', package='job_shop_lab4'):
    connectors = c.find('Connectors')
    if connectors is None: connectors = child(c, 'Connectors')
    e = common('Connector', 'connector' + uid(), int(float(a.findtext('X'))) + 30, a.findtext('Y'))
    for label, ob, port in [('Source', a, out), ('Target', b, into)]:
        r = child(e, label + 'EmbeddedObjectReference')
        child(r, 'PackageName', package); child(r, 'ClassName', c.findtext('Name')); child(r, 'ItemName', ob.findtext('Name'))
        r = child(e, label + 'ConnectableItemReference')
        child(r, 'PackageName', ob.findtext('ActiveObjectClass/PackageName'))
        child(r, 'ClassName', ob.findtext('ActiveObjectClass/ClassName')); child(r, 'ItemName', port)
    points = child(e, 'Points')
    for x, y in [(0, 0), (float(b.findtext('X'))-float(a.findtext('X'))-30, float(b.findtext('Y'))-float(a.findtext('Y')))]:
        p = child(points, 'Point'); child(p, 'X', x); child(p, 'Y', y)
    connectors.append(e)

def point(pres, name, x, y):
    e = common('PointNode', name, x, y)
    for k, v in [('DrawMode','SHAPE_DRAW_2D3D'),('Z',0),('FakeNode','false'),('Color',-14774017),('Radius',0),('SpeedLimit','false')]: child(e,k,v)
    pres.append(e)
    return e

def rectnode(pres, name, x, y, w=70, h=30):
    e = common('RectangleNode', name, x, y)
    for k,v in [('DrawMode','SHAPE_DRAW_2D3D'),('Z',0),('LineColor',-14774017),('LineWidth',1),('LineStyle','DASHED'),('AttractorsLayout','random'),('Sloped','false'),('Width',w),('Height',h),('Rotation',0)]: child(e,k,v)
    ob = descriptor('AreaNodeDescriptor',name+'_descriptor',0,0)
    for tag in ['Name','X','Y','Label','PublicFlag','PresentationFlag','ShowLabel']:
        for s in ob.findall(tag): ob.remove(s)
    e.append(ob)
    pres.append(e)
    return e

def path(pres, name, a, b):
    x,y=float(a.findtext('X')),float(a.findtext('Y'))
    dx,dy=float(b.findtext('X'))-x,float(b.findtext('Y'))-y
    e=common('Path',name,x,y,SourceId=a.findtext('Id'),TargetId=b.findtext('Id'))
    for k,v in [('DrawMode','SHAPE_DRAW_2D3D'),('Z',0),('LineColor',-14774017),('LineMaterial','null'),('LineWidth',1),('PathType','dashedLine'),('Bidirectional','true'),('SpeedLimit','false')]: child(e,k,v)
    w=child(e,'Width',Class='UnitValue'); child(w,'Value',1,Class='Double'); child(w,'Unit','METER',Class='LengthUnits')
    ps=child(e,'Points')
    for xx,yy in [(0,0),(0,0),(dx/3,dy/3),(dx,dy),(dx*2/3,dy*2/3),(0,0)]:
        p=child(ps,'Point'); child(p,'X',xx); child(p,'Y',yy); child(p,'Z',0)
    pres.append(e)
    return e

def text(pres,name,value,x,y,size=15):
    e=common('Text',name,x,y)
    for k,v in [('DrawMode','SHAPE_DRAW_2D'),('EmbeddedIcon','false'),('Z',0),('Rotation',0),('Color',-16777216),('Text',value),('Alignment','LEFT')]: child(e,k,v)
    f=child(e,'Font'); child(f,'Name','SansSerif'); child(f,'Size',size); child(f,'Style',0)
    pres.append(e)
    return e

def refs(model):
    for name, major, minor, build in [('com.anylogic.libraries.processmodeling',8,0,5),('com.anylogic.libraries.material_handling',8,3,0)]:
        if any(e.findtext('LibraryName')==name for e in model.findall('RequiredLibraryReference')): continue
        r=child(model,'RequiredLibraryReference'); child(r,'LibraryName',name); child(r,'VersionMajor',major); child(r,'VersionMinor',minor); child(r,'VersionBuild',build)

def experiment(model,horizon=480):
    e=model.find('Experiments/SimulationExperiment')
    for k,v in [('RandomNumberGenerationType','fixedSeed'),('SeedValue',1),('BypassInitialScreen','true')]: settext(e,k,v)
    props=e.find('PresentationProperties'); settext(props,'RealTimeScale',20)
    mt=e.find('ModelTimeProperties'); settext(mt,'StopOption','Stop at specified time'); settext(mt,'FinalTime',horizon)

def write(root, path):
    E.indent(root)
    path.parent.mkdir(exist_ok=True,parents=True)
    E.ElementTree(root).write(path,encoding='utf-8',xml_declaration=True)

def job_phase1():
    root=E.parse(BASE).getroot()
    model=root.find('Model'); c=model.find('ActiveObjectClasses/ActiveObjectClass')
    pres=c.find('Presentation/Level/Presentation')
    network=pres.find('Network'); np=network.find('Presentation')
    dock=rectnode(np,'receivingDock',140,220)
    parking=rectnode(np,'forkliftParking',470,220)
    left=next(e for e in np if e.findtext('Name')=='node1')
    right=next(e for e in np if e.findtext('Name')=='node5')
    path(np,'dockToStorage',dock,left); path(np,'storageToParking',right,parking)
    text(pres,'title','Job Shop - Lab4 | Fase 1',50,30,22)
    text(pres,'dockLabel','Recepción',140,270)
    text(pres,'parkingLabel','Montacargas',470,270)
    bs=[
      block(c,'Source','sourcePallets',60,370,{'arrivalType':'self.INTERARRIVAL_TIME','interarrivalTime':unit(5),'locationType':'self.LOCATION_NODE','locationNode':'receivingDock'}),
      block(c,'Store','storeRawMaterial',230,370,{'resourceType':'self.RESOURCE_NONE','storage':'storage'}),
      block(c,'Delay','rawMaterialInStorage',400,370,{'delayTime':unit('triangular(15,20,30)'),'maximumCapacity':'true'}),
      block(c,'Retrieve','retrieveRawMaterial',590,370,{'resourceType':'self.RESOURCE_NONE','destinationType':'self.DEST_NODE','destinationNode':'forkliftParking'}),
      block(c,'Sink','sink',760,370)]
    for a,b in zip(bs,bs[1:]): connect(c,a,b)
    refs(model); experiment(model,120)
    out=ROOT/'Job Shop Lab4'/'fases'/'01_almacen'/'Job Shop Lab4 Fase 1.alp'
    settext(model,'Name','Job Shop Lab4 Fase 1'); write(root,out)
    print(out)
    return root

ASSETS = Path('C:/Program Files/AnyLogic 8.9 Personal Learning Edition/plugins/com.anylogic.ui_8.9.10.202609231424/resources/3d')

def image(pres, model, package, filename, x, y, width, height):
    e=common('Image','layoutImage',x,y)
    for k,v in [('Lock','true'),('DrawMode','SHAPE_DRAW_2D3D'),('EmbeddedIcon','false'),('Z',0),('Width',width),('Height',height),('Rotation',0),('OriginalSize','false')]: child(e,k,v)
    r=child(child(e,'ImageFiles'),'ImageResourceReference'); child(r,'PackageName',package); child(r,'ClassName',filename)
    pres.insert(0,e)
    resource(model,filename)

def resource(model,path):
    rs=model.find('ModelResources')
    if rs is None: rs=child(model,'ModelResources')
    if any(r.findtext('Path')==path for r in rs): return
    r=child(rs,'Resource'); child(r,'Path',path); child(r,'ReferencedFromUserCode','false')

def fresh_class(model,name,usage='ENTITY',rotate='true'):
    c=copy.deepcopy(E.parse(BASE).find('Model/ActiveObjectClasses/ActiveObjectClass'))
    for e in c.iter('Id'): e.text=uid()
    settext(c,'Name',name); settext(c,'FlowChartsUsage',usage)
    for tag in ['EmbeddedObjects','Connectors','Presentation']:
        el=c.find(tag)
        if el is not None: el.clear()
        else: el=child(c,tag)
    level=common('Level','level')
    for k,v in [('DrawMode','SHAPE_DRAW_2D3D'),('Z',0),('LevelVisibility','DIM_NON_CURRENT')]: child(level,k,v)
    child(level,'Presentation'); c.find('Presentation').append(level)
    settext(c,'CurrentLevel',level.findtext('Id'))
    settext(c.find('AgentProperties'),'RotateAnimationTowardsMovement',rotate)
    model.find('ActiveObjectClasses').append(c)
    return c

def figure(c,model,package,name,filename,x=0,y=0,z=0,scale=1,rotation=0,visible=None):
    pres=c.find('Presentation/Level/Presentation')
    e=common('Figure3D',name,x,y)
    child(e,'DrawMode','SHAPE_DRAW_2D3D'); child(e,'Z',z)
    ref=child(e,'ResourceReference'); child(ref,'PackageName',package); child(ref,'ClassName','3d/'+filename)
    child(e,'ColorTable')
    for k,v in [('AutoScale','true'),('Scale',scale),('Rotation',rotation),('AxisOrder','YZX_AXIS_ORDER'),('ApplyShading','true'),('InternalLighting','OFF'),('IgnoreSceneLights','false')]: child(e,k,v)
    if visible: child(e,'VisibleCode',visible)
    pres.append(e); resource(model,'3d/'+filename)
    return e

def camera(pres,x=200,y=320,z=180,rx=25,rz=-25):
    e=common('Camera3D','camera',x,y); child(e,'Z',z); child(e,'RotationX',rx); child(e,'RotationZ',rz); pres.append(e)
    w=common('Control','window3d',50,620,Type='Window3D')
    for k,v in [('Width',900),('Height',450),('MakeDefaultViewArea','true'),('FollowCamera','false'),('NavigationType','limitedToZAboveZero'),('FarClippingDistance',3000),('Camera','camera')]: child(w,k,v)
    pres.append(w)

def assets_for(model,folder):
    for r in model.findall('ModelResources/Resource'):
        path=r.findtext('Path'); dest=folder/path; dest.parent.mkdir(parents=True,exist_ok=True)
        if path.startswith('3d/'):
            shutil.copy2(ASSETS/Path(path).name,dest)
        elif path=='layout.png':
            shutil.copy2(Path('C:/Program Files/AnyLogic 8.9 Personal Learning Edition/resources/AnyLogic in 3 days/Job Shop/layout.png'),dest)

def save_job(root,phase,label):
    model=root.find('Model'); settext(model,'Name',f'Job Shop Lab4 Fase {phase}')
    settext(model.find('Experiments/SimulationExperiment/PresentationProperties'),'Title',f'Job Shop Lab4 - Fase {phase} : Simulation')
    title=next(e for e in model.findall('ActiveObjectClasses/ActiveObjectClass/Presentation/Level/Presentation/Text') if e.findtext('Name')=='title')
    settext(title,'Text',f'Job Shop - Lab4 | Fase {phase}')
    dest=ROOT/'Job Shop Lab4'/'fases'/f'{phase:02d}_{label}'/f'Job Shop Lab4 Fase {phase}.alp'
    write(root,dest); assets_for(model,dest.parent)
    print(dest)

def job_all():
    root=job_phase1(); model=root.find('Model'); main=model.find('ActiveObjectClasses/ActiveObjectClass')
    pres=main.find('Presentation/Level/Presentation'); np=pres.find('Network/Presentation')
    obs={e.findtext('Name'):e for e in main.findall('EmbeddedObjects/EmbeddedObject')}
    # Fase 2: recursos móviles que trasladan pallets dentro del almacén.
    fork=block(main,'ResourcePool','forklifts',60,520,{'capacity':'5','speed':unit(1,'SpeedUnits','MPS'),'homeNodes':'{forkliftParking}'})
    for n in ['storeRawMaterial','retrieveRawMaterial']:
        setparam(obs[n],'resourceType','self.RESOURCE_PML'); setparam(obs[n],'resourcePool','forklifts')
    setparam(obs['retrieveRawMaterial'],'wrapUpTaskPolicyType','self.WRAP_UP_IF_NO_TASKS')
    save_job(root,2,'montacargas')
    # Fase 3: tipos propios y figuras de la paleta 3D, añadidas a clases vacías.
    forklift=fresh_class(model,'ForkliftTruck','RESOURCE_UNIT')
    figure(forklift,model,'job_shop_lab4','forklift','forklift.dae',x=0)
    figure(forklift,model,'job_shop_lab4','driver','sittingworker.dae',x=-5,z=8)
    pallet=fresh_class(model,'Pallet','MATERIAL_ITEM')
    figure(pallet,model,'job_shop_lab4','pallet','pallet.dae',scale=.75)
    figure(pallet,model,'job_shop_lab4','box','box_1_closed.dae',z=2,scale=1.25)
    setparam(fork,'newUnit',entity('ForkliftTruck'))
    setparam(obs['sourcePallets'],'newEntity',entity('Pallet'))
    settext(pres.find('RackStorage'),'SimplifiedAnimation','false')
    camera(pres)
    save_job(root,3,'animacion_3d')
    # Fase 4: camiones cada hora; sus pallets se generan al entrar en descarga.
    truck=fresh_class(model,'Truck','ENTITY',rotate='false')
    figure(truck,model,'job_shop_lab4','truck','truck.dae',rotation=-180)
    exitnode=point(np,'exitNode',70,300)
    dock=next(e for e in np if e.findtext('Name')=='receivingDock')
    path(np,'truckDriveway',exitnode,dock)
    trucks=[
        block(main,'Source','sourceDeliveryTrucks',60,460,{'arrivalType':'self.INTERARRIVAL_TIME','interarrivalTime':unit(1,'TimeUnits','HOUR'),'firstArrivalMode':'self.AT_START','locationType':'self.LOCATION_NODE','locationNode':'exitNode','speed':unit(40,'SpeedUnits','KPH'),'newEntity':entity('Truck')}),
        block(main,'MoveTo','drivingToDock',230,460,{'destinationNode':'receivingDock'}),
        block(main,'Delay','unloading',400,460,{'type':'self.MANUAL','entityLocation':'receivingDock','onEnter':'sourcePallets.inject(60);'}),
        block(main,'MoveTo','drivingToExit',590,460,{'destinationNode':'exitNode'}),
        block(main,'Sink','sinkTrucks',760,460)]
    for a,b in zip(trucks,trucks[1:]): connect(main,a,b)
    setparam(obs['sourcePallets'],'arrivalType','self.MANUAL')
    setparam(obs['storeRawMaterial'],'onExit','if (self.nWaitingForResource() == 0) unloading.stopDelayForAll();')
    save_job(root,4,'camiones')
    # Fase 5: dos CNC estáticos. Se reserva el CNC antes de retirar del rack.
    cncclass=fresh_class(model,'CNC','RESOURCE_UNIT')
    figure(cncclass,model,'job_shop_lab4','busyMachine','cnc_vertical_machining_center_2_state_1.dae',x=30,rotation=90,visible='isBusy()')
    figure(cncclass,model,'job_shop_lab4','idleMachine','cnc_vertical_machining_center_2_state_2.dae',x=30,rotation=90,visible='isIdle()')
    figure(cncclass,model,'job_shop_lab4','operator','worker.dae',x=0,y=-15)
    n1=point(np,'nodeCNC1',160,110); n2=point(np,'nodeCNC2',250,110)
    aisle=next(e for e in np if e.findtext('Name')=='node')
    path(np,'pathCNC1',aisle,n1); path(np,'pathCNC2',aisle,n2)
    block(main,'ResourcePool','cnc',230,520,{'type':'self.RESOURCE_STATIC','capacityDefinitionType':'self.CAPACITY_HOME_LOCATION','homeNodes':'{nodeCNC1,nodeCNC2}','newUnit':entity('CNC')})
    seize=block(main,'Seize','seizeCNC',520,370,{'resourceSets':'{{cnc}}'})
    process=block(main,'Delay','processing',820,370,{'delayTime':unit(1),'maximumCapacity':'true'})
    release=block(main,'Release','releaseCNC',960,370)
    settext(obs['retrieveRawMaterial'],'X',660); settext(obs['sink'],'X',1100)
    setparam(obs['retrieveRawMaterial'],'destinationType','self.DEST_RESOURCE')
    setparam(obs['retrieveRawMaterial'],'destinationResource','cnc')
    # Rehace los conectores de pallets para introducir la reserva y liberación.
    main.find('Connectors').clear()
    flow=[obs['sourcePallets'],obs['storeRawMaterial'],obs['rawMaterialInStorage'],seize,obs['retrieveRawMaterial'],process,release,obs['sink']]
    for a,b in zip(flow,flow[1:]): connect(main,a,b)
    for a,b in zip(trucks,trucks[1:]): connect(main,a,b)
    experiment(model,480)
    save_job(root,5,'cnc')
    settext(model,'Name','Job Shop Lab4')
    settext(model.find('Experiments/SimulationExperiment/PresentationProperties'),'Title','Job Shop Lab4 : Simulation')
    final=ROOT/'Job Shop Lab4'/'Job Shop Lab4.alp'
    write(root,final); assets_for(model,final.parent); print(final)
    return root

if __name__=='__main__':
    job_all()
