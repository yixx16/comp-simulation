"""Presentación propia; figuras estándar de la paleta, sin importar modelos resueltos."""
from build_battery import *

def panel(pres,name,x,y,w,h,color,z=-1,height=0):
    e=common('Rectangle',name,x,y)
    for k,v in [('DrawMode','SHAPE_DRAW_2D3D'),('EmbeddedIcon','false'),('Z',z),('ZHeight',height),('LineWidth',1),('LineColor',-8355712),('LineMaterial','null'),('LineStyle','SOLID'),('Width',w),('Height',h),('Rotation',0),('FillColor',color),('FillMaterial','null'),('Lock','true')]:child(e,k,v)
    pres.insert(0,e)

def polish(path,battery=False):
    root=E.parse(path).getroot();m=root.find('Model');pkg=m.findtext('JavaPackageName')
    import build_from_scratch as builder
    builder.seq=max(int(e.text) for e in root.iter('Id') if e.text and e.text.isdigit())+100
    main=next(c for c in m.findall('ActiveObjectClasses/ActiveObjectClass') if c.findtext('Name')=='Main')
    pres=main.find('Presentation/Level/Presentation')
    # Evita duplicados al aplicar de nuevo este acabado.
    for e in list(pres):
        if e.findtext('Name','').startswith('labVisual'):pres.remove(e)
    obs={e.findtext('Name'):e for e in main.findall('EmbeddedObjects/EmbeddedObject')}
    if battery:
        panel(pres,'labVisualFloor',-20,50,1160,510,-1183240)
        # Muros de presentación con altura; no modifican los caminos validados.
        for name,x,y,w,h in [('North',-20,50,1160,3),('South',-20,557,1160,3),('East',1137,50,3,510)]:panel(pres,'labVisualWall'+name,x,y,w,h,-8355712,0,20)
        machines=[('AnodePaste','pasting_machine.dae',180,130),('CathodePaste','pasting_machine.dae',180,370),('AnodeOven','drying_chamber_closed.dae',200,260),('CathodeOven','drying_chamber_closed.dae',200,500),('Wrapper','plate_enveloper.dae',460,160),('Assembly','COS_part_1.dae',620,160),('Cap','heat_sealing_machine.dae',710,300),('QA','leakage_testing_machine.dae',760,300),('Fill','filling_machine.dae',890,300)]
        for name,asset,x,y in machines:figure(main,m,pkg,'labVisual'+name,asset,x,y,0,scale=.2)
        for name,label,x,y in [('Anode','Ánodos: recubrimiento y curado',20,65),('Cathode','Cátodos: recubrimiento y curado',20,345),('Groups','Envoltura y grupos de 15 + 15',430,100),('Finish','Caja → QA → electrolito → carga',650,270),('Defect','Rechazadas (1 %)',790,410),('Store','Área de carga',1010,270)]:text(pres,'labVisualLabel'+name,label,x,y,13)
        # Flujo completo visible en una sola pantalla, con dos entradas al Combine.
        positions={'prepareAnode':(40,650),'wrappingConvey':(160,650),'assembler':(280,650),'hold':(400,650),'toCase':(520,650),'combine':(640,650),'conveyBattery':(760,650),'toLoadingArea':(880,650),'toChargingArea':(1000,650),'sink':(1120,650),'prepareCathode':(160,735),'batterySource':(280,580),'caseQueue':(400,580),'conveyorEnter':(520,580),'conveyDefective':(760,745),'sinkDefective':(900,745),'forklifts':(50,825),'operator':(240,825),'AGVs':(400,825)}
        settext(pres.find('Control'),'Y',930)
    else:
        panel(pres,'labVisualFloor',30,65,550,250,-1183240)
        for name,x,y,w,h in [('North',30,65,550,3),('East',577,65,3,250),('South',180,312,400,3)]:panel(pres,'labVisualWall'+name,x,y,w,h,-8355712,0,20)
        positions={'sourcePallets':(60,380),'storeRawMaterial':(200,380),'rawMaterialInStorage':(340,380),'seizeCNC':(480,380),'retrieveRawMaterial':(620,380),'processing':(760,380),'releaseCNC':(900,380),'sink':(1040,380)}
        text(pres,'labVisualProcess','60 pallets por camión · 5 montacargas · 2 CNC',50,340,15)
    for name,(x,y) in positions.items():
        if name in obs:settext(obs[name],'X',x);settext(obs[name],'Y',y)
    # Redibuja únicamente la geometría de los conectores existentes.
    for conn in main.findall('Connectors/Connector'):
        sn=conn.findtext('SourceEmbeddedObjectReference/ItemName');tn=conn.findtext('TargetEmbeddedObjectReference/ItemName')
        if sn not in obs or tn not in obs:continue
        sx=float(obs[sn].findtext('X'));sy=float(obs[sn].findtext('Y'));tx=float(obs[tn].findtext('X'));ty=float(obs[tn].findtext('Y'))
        settext(conn,'X',sx);settext(conn,'Y',sy);pts=conn.find('Points');pts.clear()
        for x,y in [(0,0),(tx-sx,ty-sy)]:p=child(pts,'Point');child(p,'X',x);child(p,'Y',y)
    # Indicadores disponibles en la presentación durante Simulation.
    for i,(name,label,expression) in enumerate([('Entered','Entradas admitidas','labEntered'),('Good','Salidas conformes','labGood'),('Wip','WIP actual','labWip'),('Defect','Rechazadas','labDefective')]):
        e=text(pres,'labVisualKPI'+name,label+': 0',650+120*i,825 if battery else 550,13)
        e=pres[-1];child(e,'TextCode','"'+label+': " + '+expression)
    for exp in m.findall('Experiments/SimulationExperiment'):
        settext(exp.find('PresentationProperties'),'Width',1200);settext(exp.find('PresentationProperties'),'Height',850)
        settext(exp.find('PresentationProperties'),'Title',m.findtext('Name')+' : Simulation')
    write(root,path);assets_for(m,path.parent)

if __name__=='__main__':
    polish(ROOT/'Job Shop Lab4'/'Job Shop Lab4.alp')
    polish(DEST/'Lead Acid Battery Lab4.alp',True)
