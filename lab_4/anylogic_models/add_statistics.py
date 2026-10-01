"""Instrumentación y experimentos nativos: resultados reales de AnyLogic."""
from build_battery import *

def instrument(path,model_key,battery=False):
    root=E.parse(path).getroot();m=root.find('Model');pkg=m.findtext('JavaPackageName')
    import build_from_scratch as builder
    builder.seq=max(int(e.text) for e in root.iter('Id') if e.text and e.text.isdigit())+100
    main=next(e for e in m.findall('ActiveObjectClasses/ActiveObjectClass') if e.findtext('Name')=='Main')
    output=(ROOT.parent/'datos'/'anylogic'/'replicas').resolve().as_posix()
    code='''
public long labSeed = 1;
public int labEntered=0, labCompleted=0, labGood=0, labDefective=0, labWip=0;
public double labLast=0, labArea=0, labSum=0, labSum2=0;
public java.util.IdentityHashMap<Agent,Double> labArrivals = new java.util.IdentityHashMap<>();
public void labUpdate() { labArea += labWip*(time()-labLast); labLast=time(); }
public void labEnter(Agent a) { labUpdate(); labWip++; labEntered++; labArrivals.put(a,time()); }
public void labExit(Agent a, boolean defective) {
    labUpdate(); labWip--; labCompleted++; if(defective) labDefective++; else labGood++;
    Double start=labArrivals.remove(a);
    if(start==null) throw new IllegalStateException("Salida sin entrada estadistica");
    double duration=time()-start; labSum+=duration; labSum2+=duration*duration;
}
public void writeLabStats() {
    labUpdate();
    if(Math.abs(time()-HORIZON)>0.001) return; // No exportar corridas incompletas.
    if(labEntered != labCompleted+labWip) throw new IllegalStateException("Balance de agentes incorrecto");
    try {
        java.nio.file.Path dir=java.nio.file.Paths.get("OUTPUT"); java.nio.file.Files.createDirectories(dir);
        String header="model,seed,horizon,entered,completed,good,defective,wip,mean_cycle,mean_wip,resource_utilization\\n";
        String row="MODEL,"+labSeed+","+time()+","+labEntered+","+labCompleted+","+labGood+","+labDefective+","+labWip+","+(labCompleted>0?labSum/labCompleted:Double.NaN)+","+(labArea/time())+","+UTIL+"\\n";
        java.nio.file.Files.writeString(dir.resolve("MODEL_"+labSeed+".csv"), header+row);
    } catch (java.io.IOException e) { throw new RuntimeException(e); }
}
'''.replace('HORIZON','14400' if battery else '480').replace('OUTPUT',output).replace('MODEL',model_key).replace('UTIL','operator.utilization()' if battery else 'cnc.utilization()')
    settext(main,'AdditionalClassCode',code)
    obs={e.findtext('Name'):e for e in main.findall('EmbeddedObjects/EmbeddedObject')}
    setparam(obs['batterySource' if battery else 'sourcePallets'],'onExit','labEnter(agent);',pkg)
    setparam(obs['sink'],'onEnter','labExit(agent,false);',pkg)
    if battery:setparam(obs['sinkDefective'],'onEnter','labExit(agent,true);',pkg)
    sim=m.find('Experiments/SimulationExperiment')
    settext(sim,'AfterSimulationRunCode','root.writeLabStats();')
    settext(sim.find('ModelTimeProperties'),'FinalTime',14400 if battery else 480)
    settext(sim,'ExecutionMode','realTimeScaled')
    settext(sim.find('PresentationProperties'),'ExecutionMode','realTimeScaled')
    # Plantilla del experimento vacío y su UI creada directamente en AnyLogic.
    exp=E.parse(ROOT/'experimento_creado_en_app.xml').getroot()
    exp.set('ActiveObjectClassId',main.findtext('Id'))
    for e in exp.iter('Id'):e.text=uid()
    for k,v in [('Name','Estadistica'),('AllowParallelEvaluations','false'),('UseFreeformParameters','true'),('NumberOfRuns',20),('BeforeSimulationRunCode','root.labSeed = 160005010L + getCurrentIteration(); root.getEngine().getDefaultRandomGenerator().setSeed(root.labSeed);'),('AfterSimulationRunCode','root.writeLabStats();')]:settext(exp,k,v)
    settext(exp.find('ModelTimeProperties'),'FinalTime',14400 if battery else 480)
    settext(exp.find('PresentationProperties'),'Title',model_key+' - 20 replicas')
    settext(exp.find('Presentation/Text'),'Text',model_key+(' - 20 replicas de 4 h' if battery else ' - 20 replicas de 8 h'))
    for old in m.findall('Experiments/ParamVariationExperiment'):m.find('Experiments').remove(old)
    m.find('Experiments').append(exp)
    # El experimento empieza al abrirse, sin interacción con el navegador de ejecución.
    settext(exp,'InitialSetupCode','run();')
    settext(exp,'AdditionalClassCode','@Override public void onError(Throwable error, Agent root) { error.printStackTrace(); super.onError(error, root); }')
    write(root,path)
    return root

if __name__=='__main__':
    instrument(ROOT/'Job Shop Lab4'/'Job Shop Lab4.alp','job_shop')
    instrument(DEST/'Lead Acid Battery Lab4.alp','battery',True)
