"""Modelo propio, creado desde un lienzo vacío con parámetros de la guía local.
No copia clases, conexiones ni geometría de modelos resueltos.
"""
from build_from_scratch import *

PKG='lead_acid_battery_lab4'
DEST=ROOT/'Lead Acid Battery Lab4'

def generic(e,t):
    p=e.find('GenericParameterSubstitute')
    if p is not None:
        v=child(p,'GenericParameterSubstituteValue',Class='CodeValue');child(v,'Code',t)
    return e

def embedded_shape(kind,name,params,t=None):
    e=descriptor(kind,name,0,0,params)
    if t:generic(e,t)
    for tag in ['Id','Name','X','Y','Label','PublicFlag','PresentationFlag','ShowLabel']:
        for s in e.findall(tag):e.remove(s)
    return e

def uv(e,tag,value):
    v=child(e,tag,Class='UnitValue');child(v,'Value',value,Class='Double');child(v,'Unit','METER',Class='LengthUnits')

def points(e,dx,dy=0):
    ps=child(e,'Points')
    for x,y in [(0,0),(0,0),(dx/3,dy/3),(dx,dy),(dx*2/3,dy*2/3),(0,0)]:
        p=child(ps,'Point');child(p,'X',x);child(p,'Y',y);child(p,'Z',0)

def network(pres,name,tag='ConveyorNetwork'):
    n=common(tag,name);child(n,'DrawMode','SHAPE_DRAW_2D3D');child(n,'Z',0);pres.append(n)
    return child(n,'Presentation')

def conveyor(np,name,x,y,dx,dy=0,t='Electrode',speed=None):
    e=common('Conveyor',name,x,y);child(e,'DrawMode','SHAPE_DRAW_2D3D');child(e,'Z',20)
    pars={} if speed is None else {'maxSpeed':unit(speed,'SpeedUnits','MPS'),'initialSpeed':unit(speed,'SpeedUnits','MPS')}
    e.append(embedded_shape('ConveyorPathDescriptor',name,pars,t));uv(e,'Width',.5)
    for k,v in [('LineColor',-8355712),('LineMaterial','null'),('DrawStands','true'),('StandsLevel',0),('IsObstacle','true')]:child(e,k,v)
    points(e,dx,dy);child(e,'Presentation');np.append(e);return e

def station(conv,name,offset,length,time,capacity=1,action='',t='Electrode'):
    e=common('ConveyorSimpleStation',name);child(e,'DrawMode','SHAPE_DRAW_2D3D');child(e,'Z',0);child(e,'VisibleCode','false')
    e.append(embedded_shape('ConveyorSimpleStationDescriptor',name,{'processTime':time,'capacity':str(capacity),'onProcessFinished':action},t))
    child(e,'Offset',offset);uv(e,'Length',length)
    for k,v in [('LineColor',-16777216),('FillColor',-8355712),('LineMaterial','null'),('FillMaterial','null')]:child(e,k,v)
    conv.find('Presentation').append(e);return e

def variable(c,name,t,initial,parameter=False):
    vs=c.find('Variables')
    if vs is None:vs=child(c,'Variables')
    e=common('Variable',name,40,80+40*len(vs),Class='Parameter' if parameter else 'PlainVariable')
    if parameter:
        p=child(e,'Properties',SaveInSnapshot='false',ModificatorType='STATIC');child(p,'Type',t);child(p,'UnitType','NONE');child(p,'SdArray','false')
        ed=child(p,'ParameterEditor');child(ed,'Id',uid());child(ed,'Name','null');child(ed,'Label',name);child(ed,'EditorContolType','TEXT_BOX')
        if initial is not None:child(child(p,'DefaultValue',Class='CodeValue'),'Code',initial)
    else:
        p=child(e,'Properties',SaveInSnapshot='true',Constant='false',AccessType='public',StaticVariable='false');child(p,'Type',t);child(child(p,'InitialValue',Class='CodeValue'),'Code',initial)
    vs.append(e);return e

def dimensions(c,l,w,h,scale=100):
    ap=c.find('AgentProperties')
    for k,v in [('PhysicalLength',l),('PhysicalWidth',w),('PhysicalHeight',h)]:
        p=ap.find(k);p.clear();p.set('Class','CodeUnitValue');child(p,'Code',v);child(p,'Unit','METER',Class='LengthUnits')
    s=c.find('ScaleRuler');settext(s,'Length',100);settext(s,'ModelLength',100/scale);settext(s,'Scale',scale);settext(s,'InheritedFromParentAgentType','false')

def rectangle(c,name,w,h,zheight,color,dynamic=None):
    p=c.find('Presentation/Level/Presentation');e=common('Rectangle',name,-w/2,-h/2)
    for k,v in [('DrawMode','SHAPE_DRAW_2D3D'),('EmbeddedIcon','false'),('Z',0),('ZHeight',zheight),('LineWidth',0),('LineColor',-1),('LineMaterial','null'),('LineStyle','SOLID'),('Width',w),('Height',h),('Rotation',0),('FillColor',color),('FillMaterial','null')]:child(e,k,v)
    if dynamic:child(e,'FillColorCode',dynamic)
    p.append(e)

def event(c,name,first,repeat,code):
    es=c.find('Events')
    if es is None:es=child(c,'Events')
    e=common('Event',name,200,500);p=child(e,'Properties',TriggerType='timeout',Mode='cyclic' if repeat else 'once')
    for tag,val in [('Timeout',first),('OccurrenceTime',first),('RecurrenceCode',repeat or first)]:
        v=child(p,tag,Class='CodeUnitValue');child(v,'Code',val);child(v,'Unit','SECOND',Class='TimeUnits')
    child(p,'OccurrenceAtTime','true');child(p,'Condition','false');child(e,'Action',code);es.append(e)

def cranelayout(pres,name,x,y,t):
    e=common('Crane',name,x,y);child(e,'DrawMode','SHAPE_DRAW_2D3D');child(e,'Z',0)
    e.append(embedded_shape('JibCraneDescriptor',name,{},t))
    uv(e,'JibLength',3);uv(e,'CraneHeight',4);uv(e,'TrolleyLocation',3)
    for k,v in [('CabinColor',-8355712),('Color',-2448096),('BlockedZoneEnabled','true'),('BlockedZoneStartAngle',0),('BlockedZoneAngle',45),('JibAngle',0),('CraneType','industrial'),('IsObstacle','true')]:child(e,k,v)
    pres.append(e);return e

def ck(c,a,b,out='out',into='in'):
    connect(c,a,b,out,into,PKG)

def b(c,k,n,x,y,params=None,t=None):
    e=block(c,k,n,x,y)
    for key,value in (params or {}).items():setparam(e,key,value,PKG)
    if t:generic(e,t)
    return e

def node(pres,name,x,y,w=60,h=40,z=0):
    n=rectnode(pres,name,x,y,w,h);settext(n,'AttractorsLayout','arranged');settext(n,'Z',z);child(n,'VisibleCode','false');return n

def save(root,phase):
    m=root.find('Model');settext(m,'Name',f'Lead Acid Battery Lab4 Fase {phase}')
    settext(m.find('Experiments/SimulationExperiment/PresentationProperties'),'Title',f'Lead Acid Battery Lab4 - Fase {phase}')
    dest=DEST/'fases'/f'{phase:02d}'/f'Lead Acid Battery Lab4 Fase {phase}.alp';write(root,dest);assets_for(m,dest.parent)
    print(dest)

def build():
    root=E.parse(BASE).getroot();m=root.find('Model');settext(m,'Id',uid());settext(m,'JavaPackageName',PKG);settext(m,'ModelTimeUnit','Second')
    for e in root.iter('PackageName'):
        if e.text=='job_shop_lab4':e.text=PKG
    main=m.find('ActiveObjectClasses/ActiveObjectClass');settext(main,'Id',uid())
    for e in root.iter():
        if 'ActiveObjectClassId' in e.attrib:e.set('ActiveObjectClassId',main.findtext('Id'))
    for tag in ['EmbeddedObjects','Connectors']:
        e=main.find(tag)
        if e is None:child(main,tag)
        else:e.clear()
    pres=main.find('Presentation/Level/Presentation');pres.clear()
    dimensions(main,1,1,1,20);refs(m);experiment(m,14400)
    for k,v in [('com.anylogic.libraries.fluid',8)]:
        r=child(m,'RequiredLibraryReference');child(r,'LibraryName',k);child(r,'VersionMajor',v);child(r,'VersionMinor',0);child(r,'VersionBuild',3)
    DEST.mkdir(exist_ok=True);write(root,DEST/'inicio_vacio.alp')
    text(pres,'title','Lead Acid Battery Production - Lab4',30,25,22)
    # Fase 1: 200 electrodos cada 1.5 h, recubrimiento y lotes de 100.
    el=fresh_class(m,'Electrode','MATERIAL_ITEM');dimensions(el,.3,.3,.005);variable(el,'color','Color','white');rectangle(el,'rectangle',30,30,.5,-1,'color')
    plates=fresh_class(m,'PlatesBatch','MATERIAL_ITEM');dimensions(plates,1.2,1.2,.35);figure(plates,m,PKG,'pallet','pallet.dae');rectangle(plates,'plates',100,100,30,-3308225)
    cn=network(pres,'anodeNetwork');conv=conveyor(cn,'conveyor',100,130,220)
    station(conv,'pastingMachine',80,.5,unit(1,'TimeUnits','SECOND'),action='agent.color = peru;')
    node(pres,'platesBuffer',320,130);camera(pres,x=480,y=450,z=500);settext(pres.find("Control"),'Y',1000)
    src=b(main,'Source','source',40,610,{'arrivalType':'self.INTERARRIVAL_TIME','interarrivalTime':unit(1.5,'TimeUnits','HOUR'),'firstArrivalMode':'self.AT_START','multipleEntitiesPerArrival':'true','entitiesPerArrival':'200','pushProtocol':'false','newEntity':entity('Electrode')},'Electrode')
    co=b(main,'Convey','convey',190,610,{'sourceConveyor':'conveyor','targetConveyor':'conveyor','removeFromConveyor':'true'},'Electrode')
    ba=b(main,'Batch','batch',340,610,{'batchSize':'100','permanent':'false','entityLocation':'platesBuffer','locationType':'self.LOCATION_NODE','locationNode':'platesBuffer','newBatch':entity('PlatesBatch')},'Agent')
    sink=b(main,'Sink','sink',1900,750);flow=[src,co,ba];
    def reflow():
        main.find('Connectors').clear()
        for a,z in zip(flow,flow[1:]):ck(main,a,z)
        ck(main,flow[-1],sink)
    reflow();save(root,1)
    # Fase 2: transporte libre con dos montacargas y curado de demostración.
    fl=fresh_class(m,'Forklift','TRANSPORTER');dimensions(fl,2,1.3,1.5,20);settext(fl,'StartupCode','setCargoPosition(1, 0, 0, METER);');figure(fl,m,PKG,'forklift','forklift.dae')
    node(pres,'forkliftsHomeLocation',70,430,100,50);node(pres,'curingOven',120,230,200,60);node(pres,'preassembleElectrodeBuffer',380,70)
    fleet=b(main,'TransporterFleet','forklifts',60,900,{'capacity':'2','navigationType':'self.FREE_SPACE_NAVIGATION','homeNodes':'{forkliftsHomeLocation}','turnRadius':unit(1,'LengthUnits','METER'),'newTransporter':entity('Forklift'),'maximumSpeed':unit(.5,'SpeedUnits','MPS')},'Forklift')
    to=b(main,'MoveByTransporter','toOven',490,610,{'destinationNode':'curingOven','fleet':'forklifts','loadingTime':unit(1),'unloadingTime':unit(1)},'PlatesBatch')
    de=b(main,'Delay','curing',640,610,{'delayTime':unit(2)},'PlatesBatch')
    tb=b(main,'MoveByTransporter','toElectrodeBuffer',790,610,{'destinationNode':'preassembleElectrodeBuffer','fleet':'forklifts','loadingTime':unit(.5),'unloadingTime':unit(.5)},'PlatesBatch')
    flow += [to,de,tb];reflow();save(root,2)
    # Fase 3: separación temporal del lote, envoltura y ensamblaje de 15 placas.
    wn=network(pres,'wrappingNetwork');wc=conveyor(wn,'wrappingConveyor',380,160,200)
    station(wc,'wrappingStation',80,.5,unit(1,'TimeUnits','SECOND'),action='agent.color = white;')
    node(pres,'wrappedElectrodeBuffer',580,160,25,20,20);node(pres,'assembleArea',620,160,15,20,20);node(pres,'assembledBlocksBuffer',660,190,20,20,20)
    op=fresh_class(m,'Operator','RESOURCE_UNIT');figure(op,m,PKG,'worker','worker.dae');on=point(pres,'operatorLocation',620,210)
    b(main,'ResourcePool','operator',250,900,{'type':'self.RESOURCE_STATIC','capacity':'1','homeNodes':'{operatorLocation}','newUnit':entity('Operator')},'Operator')
    group=fresh_class(m,'BatteryBlock','MATERIAL_ITEM');dimensions(group,.3,.3,.2)
    rectangle(group,'groups',30,30,20,-3308225)
    un=b(main,'Unbatch','unbatchElectrodes',940,610,{'sameAsBatchLocation':'false','locationType':'self.LOCATION_XYZ','locationX':'wrappingConveyor.getStartPoint().x','locationY':'wrappingConveyor.getStartPoint().y','locationZ':'20'},'Electrode')
    wr=b(main,'Convey','wrappingConvey',1090,610,{'sourceConveyor':'wrappingConveyor','targetConveyor':'wrappingConveyor','removeFromConveyor':'true'},'Electrode')
    ass=b(main,'Assembler','assembler',1240,610,{'quantity1':'15','quantity2':'0','newEntity':entity('BatteryBlock'),'delayTime':unit(5),'outputBufferCapacity':'1','locationType':'self.LOCATION_NODE','locationNode':'assembledBlocksBuffer','entityLocationDelay':'assembleArea','resourceSets':'{{operator}}'},'Agent')
    flow += [un,wr,ass];reflow();main.find('Connectors')[-2].find('TargetConnectableItemReference/ItemName').text='in1';save(root,3)
    # Fase 4: sincronización caja/grupo con Hold, grúa y Combine.
    battery=fresh_class(m,'Battery','MATERIAL_ITEM');dimensions(battery,.3,.2,.15);rectangle(battery,'caseShape',30,20,15,-16777216)
    bn=network(pres,'batteryNetwork');bc=conveyor(bn,'batteryConveyor',650,300,240,t='Battery',speed=.5)
    pos=common('PositionOnConveyor','blockInputPosition',670,300);child(pos,'DrawMode','SHAPE_DRAW_2D3D');child(pos,'Z',0);pos.append(embedded_shape('PositionOnConveyorDescriptor','position',{},'Battery'));child(pos,'Offset',20);bc.find('Presentation').append(pos)
    node(pres,'caseBuffer',650,340);cranelayout(pres,'batteryBlockCrane',675,245,'BatteryBlock')
    bs=b(main,'Source','batterySource',1240,520,{'rate':unit(10,'RateUnits','PER_HOUR'),'locationType':'self.LOCATION_NODE','locationNode':'caseBuffer','newEntity':entity('Battery'),'pushProtocol':'false'},'Battery')
    q=b(main,'Queue','caseQueue',1390,520,{'capacity':'25','entityLocation':'caseBuffer'},'Battery')
    ce=b(main,'ConveyorEnter','conveyorEnter',1540,520,{'positionType':'self.POSITION_ON_CONVEYOR','positionOnConveyor':'blockInputPosition','onEnter':'hold.unblock();'},'Battery')
    ho=b(main,'Hold','hold',1390,610,{'mode':'self.BLOCK_AFTER_N_ENTITIES','initiallyBlocked':'true'},'BatteryBlock')
    tc=b(main,'MoveByCrane','toCase',1540,610,{'crane':'batteryBlockCrane','destinationType':'self.DEST_AGENT','destinationAgent':'blockInputPosition.getAgent()','loadingTime':unit(5,'TimeUnits','SECOND'),'unloadingTime':unit(5,'TimeUnits','SECOND')},'BatteryBlock')
    combine=b(main,'Combine','combine',1690,610,{'combineMode':'self.ENTITY1'},'Agent');flow += [ho,tc,combine];reflow()
    def additional():
        ck(main,bs,q);ck(main,q,ce);ck(main,ce,combine,into='in1')
        for conn in main.findall('Connectors/Connector'):
            target=conn.findtext('TargetEmbeddedObjectReference/ItemName')
            if target=='assembler':settext(conn.find('TargetConnectableItemReference'),'ItemName','in1')
            if target=='combine' and conn.findtext('SourceEmbeddedObjectReference/ItemName')=='toCase':settext(conn.find('TargetConnectableItemReference'),'ItemName','in2')
    additional();save(root,4)
    # Fase 5: estaciones de tapa/terminales, QA y desvío del 1%.
    station(bc,'addCapAndTerminalsStation',60,1,unit(1),t='Battery')
    station(bc,'qaStation',110,1,unit('uniform(20,30)','TimeUnits','SECOND'),action='if(randomTrue(0.01)) conveyBattery.cancel(agent);',t='Battery')
    turn=common('Turntable','turntable',800,300);child(turn,'DrawMode','SHAPE_DRAW_2D3D');child(turn,'Z',20);turn.append(embedded_shape('ConveyorTurntableDescriptor','turntable',{},'Battery'));uv(turn,'Diameter',1);child(turn,'Rotation',0);bn.append(turn)
    # Las cintas terminan en el borde del plato (radio 10 px), no en su centro.
    bc.set('TargetId',turn.findtext('Id'));bc.find('Points').clear();bc.remove(bc.find('Points'));points(bc,140)
    good=conveyor(bn,'batteryConveyor1',810,300,170,t='Battery',speed=.5);good.set('SourceId',turn.findtext('Id'))
    bad=conveyor(bn,'defectiveBatteryConveyor',800,310,0,80,t='Battery',speed=.5);bad.set('SourceId',turn.findtext('Id'))
    station(good,'electrolyteFillingStation',70,2.5,unit(2),capacity=3,t='Battery')
    cb=b(main,'Convey','conveyBattery',1840,610,{'sourceType':'self.SOURCE_CURRENT_POSITION','targetConveyor':'batteryConveyor1','removeFromConveyor':'true'},'Battery')
    cd=b(main,'Convey','conveyDefective',1840,830,{'sourceType':'self.SOURCE_CURRENT_POSITION','targetConveyor':'defectiveBatteryConveyor','removeFromConveyor':'true'},'Battery');sd=b(main,'Sink','sinkDefective',2050,830)
    flow += [cb];reflow();additional()
    def defects():ck(main,cb,cd,out='outRedirect');ck(main,cd,sd)
    defects();save(root,5)
    # Fase 6: segunda grúa y AGV guiado hasta el área de carga.
    cranelayout(pres,'batteryCrane',1000,350,'Battery');node(pres,'agvLoadingArea',980,300,40,40)
    np=network(pres,'agvNetwork','Network');home=node(np,'agvHomeLocation',1060,430,70,40);store=node(np,'store',1080,300,100,70);pp=point(np,'agvUnloadingPoint',1040,350)
    path(np,'pathHome',home,pp);path(np,'pathStore',pp,store)
    b(main,'TransporterFleet','AGVs',440,900,{'capacity':'1','homeNodes':'{agvHomeLocation}','newTransporter':entity('Forklift')},'Forklift')
    lc=b(main,'MoveByCrane','toLoadingArea',1990,610,{'crane':'batteryCrane','destinationNode':'agvLoadingArea','loadingTime':unit(5,'TimeUnits','SECOND'),'unloadingTime':unit(5,'TimeUnits','SECOND')},'Battery')
    ch=b(main,'MoveByTransporter','toChargingArea',2140,610,{'destinationNode':'store','fleet':'AGVs','loadingTime':unit(5,'TimeUnits','SECOND'),'unloadingTime':unit(5,'TimeUnits','SECOND')},'Battery')
    settext(sink,'X',2290);settext(sink,'Y',610);flow += [lc,ch];reflow();additional();defects();save(root,6)
    # Fase 7: bloque propio parametrizado, compartido por ánodos y cátodos.
    opts=child(m,'OptionLists');opt=child(opts,'OptionList');child(opt,'Id',uid());child(opt,'Name','ElectrodeType')
    for n in ['ANODE','CATHODE']:
        o=child(opt,'Option');child(o,'Id',uid());child(o,'Name',n)
    variable(plates,'electrodeType','ElectrodeType',None,True)
    settext(plates.find('Presentation/Level/Presentation/Rectangle'),'FillColorCode','electrodeType == ANODE ? peru : silver')
    can=network(pres,'cathodeNetwork');cc=conveyor(can,'cathodeConveyor',100,370,220)
    station(cc,'cathodeCoatingStation',80,.5,unit(1,'TimeUnits','SECOND'),action='agent.color = silver;')
    node(pres,'cathodePlatesBuffer',320,370);node(pres,'cathodeCuringOven',120,470,200,60);node(pres,'preassembleCathodesBuffer',380,420)
    for ob in [ass,combine,ba]:
        gv=ob.find('GenericParameterSubstitute/GenericParameterSubstituteValue/Code')
        if gv is not None:gv.text='Agent'
    prep=fresh_class(m,'PrepareElectrode','ENTITY')
    for name,typ in [('sourceConveyor','ConveyorPath'),('platesLocation','RectangularNode'),('oven','RectangularNode'),('buffer','RectangularNode'),('fleet','TransporterFleet'),('outputX','double'),('outputY','double'),('electrodeType','ElectrodeType')]:variable(prep,name,typ,None,True)
    port=common('Port','out',1140,100)
    for k,v in [('IncomingMessageType','Object'),('OutgoingMessageType','Object'),('CustomPort','false')]:child(port,k,v)
    child(prep,'Ports').append(port)
    icon=common('Rectangle','blockIcon',0,0)
    for k,v in [('DrawMode','SHAPE_DRAW_2D'),('EmbeddedIcon','true'),('Width',60),('Height',40),('FillColor',-12012417),('LineColor',-16777216)]:child(icon,k,v)
    prep.find('Presentation/Level/Presentation').append(icon)
    for ob in [src,co,ba,to,de,tb,un]:
        main.find('EmbeddedObjects').remove(ob);prep.find('EmbeddedObjects').append(ob);settext(ob,'Y',100)
    for ob,params in [(co,{'sourceConveyor':'sourceConveyor','targetConveyor':'sourceConveyor'}),(ba,{'entityLocation':'platesLocation','locationNode':'platesLocation','newBatch':'new PlatesBatch(electrodeType)'}),(to,{'destinationNode':'oven','fleet':'fleet'}),(tb,{'destinationNode':'buffer','fleet':'fleet'}),(un,{'locationX':'outputX','locationY':'outputY'})]:
        for key,val in params.items():setparam(ob,key,val,PKG)
    for a,z in zip([src,co,ba,to,de,tb,un],[co,ba,to,de,tb,un]):ck(prep,a,z)
    cn=common('Connector','toOutput',970,100);r=child(cn,'SourceEmbeddedObjectReference')
    for k,v in [('PackageName',PKG),('ClassName','PrepareElectrode'),('ItemName','unbatchElectrodes')]:child(r,k,v)
    r=child(cn,'SourceConnectableItemReference')
    for k,v in [('PackageName','com.anylogic.libraries.processmodeling'),('ClassName','Unbatch'),('ItemName','out')]:child(r,k,v)
    child(cn,'TargetId',port.findtext('Id'));pts=child(cn,'Points')
    for x in [0,170]:p=child(pts,'Point');child(p,'X',x);child(p,'Y',0)
    prep.find('Connectors').append(cn)
    def instance(name,y,anode):
        e=common('EmbeddedObject',name,940,y);settext(e,'ShowLabel','true');r=child(e,'ActiveObjectClass');child(r,'PackageName',PKG);child(r,'ClassName','PrepareElectrode')
        child(e,'Parameters');child(e,'ReplicationFlag','false');child(child(e,'Replication',Class='CodeValue'),'Code',1);child(e,'CollectionType','ARRAY_LIST_BASED');child(e,'InitialLocationType','AT_ANIMATION_POSITION')
        vals={'sourceConveyor':'conveyor' if anode else 'cathodeConveyor','platesLocation':'platesBuffer' if anode else 'cathodePlatesBuffer','oven':'curingOven' if anode else 'cathodeCuringOven','buffer':'preassembleElectrodeBuffer' if anode else 'preassembleCathodesBuffer','fleet':'forklifts','outputX':'wrappingConveyor.getStartPoint().x' if anode else 'wrappingConveyor.getEndPoint().x','outputY':'wrappingConveyor.getStartPoint().y' if anode else 'wrappingConveyor.getEndPoint().y','electrodeType':'ANODE' if anode else 'CATHODE'}
        for k,v in vals.items():setparam(e,k,v,PKG)
        main.find('EmbeddedObjects').append(e);return e
    pa=instance('prepareAnode',610,True);pc=instance('prepareCathode',710,False)
    setparam(ass,'quantity2','15',PKG);flow=[pa,wr,ass,ho,tc,combine,cb,lc,ch];reflow();additional();defects();ck(main,pc,ass,into='in2');save(root,7)
    # Fase 8: rollos de 0.075 m³ cada dos horas; conversión fluido -> agente.
    for name,x,y in [('leadMetalConveyor',0,130),('leadDioxideMetalConveyor',0,370)]:
        belt=common('BulkConveyorBelt',name,x,y)
        for k,v in [('DrawMode','SHAPE_DRAW_2D3D'),('Z',20),('LineColor',-12566464),('LineMaterial','null'),('Width',10),('DrawStands','true'),('StandsLevel',0)]:child(belt,k,v)
        points(belt,100);pres.append(belt)
    variable(prep,'metalBulkConveyor','BulkConveyorBelt',None,True)
    setparam(pa,'metalBulkConveyor','leadMetalConveyor',PKG);setparam(pc,'metalBulkConveyor','leadDioxideMetalConveyor',PKG)
    prep.find('EmbeddedObjects').remove(src);prep.find('Connectors').clear()
    ms=b(prep,'FluidSource','metalSource',40,100,{'rate':unit(5,'FlowRateUnits','CUBIC_METER_PER_SECOND'),'infiniteCapacity':'false','initialAmount':unit(.075,'AmountUnits','CUBIC_METER'),'customBatch':'true','customBatchColor':'true','batchColor':'deepSkyBlue'})
    mc=b(prep,'BulkConveyor','conveyMetal',190,100,{'length':unit(10,'LengthUnits','METER'),'speed':unit(1,'SpeedUnits','MPS'),'maxInputRate':unit(.0001,'FlowRateUnits','CUBIC_METER_PER_SECOND'),'bulkConveyorBelt':'metalBulkConveyor'})
    fa=b(prep,'FluidToAgent','fluidToAgent',340,100,{'fluidInAgent':unit(.0002,'AmountUnits','CUBIC_METER'),'newAgent':entity('Electrode')},'Electrode')
    for i,ob in enumerate([co,ba,to,de,tb,un]):settext(ob,'X',490+150*i)
    for a,z in zip([ms,mc,fa,co,ba,to,de,tb],[mc,fa,co,ba,to,de,tb,un]):ck(prep,a,z)
    settext(port,'X',1440);settext(cn,'X',1270);prep.find('Connectors').append(cn)
    event(prep,'addRoll',7200,7200,'metalSource.inject(0.075);');save(root,8)
    settext(m,'Name','Lead Acid Battery Lab4');final=DEST/'Lead Acid Battery Lab4.alp';write(root,final);assets_for(m,DEST)
    return root

if __name__=='__main__':build()



