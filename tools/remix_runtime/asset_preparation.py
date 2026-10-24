"""Bounded worker-only two-stage preparation. Coordinator owns all catalog state.
Workers return immutable results;aliases never wait on other executor tasks.
"""
from concurrent.futures import ThreadPoolExecutor
import threading
import time

WORKERS=4
MAX_JOBS=64


class PreparationQueue:
    def __init__(self,identify,prepare,workers=WORKERS):
        if not 1<=workers<=WORKERS:raise ValueError('Preparation worker bound')
        self.identify=identify;self.prepare=prepare;self.workers=workers
        self.executor=ThreadPoolExecutor(max_workers=workers,thread_name_prefix='SFC-assets')
        self.jobs={};self.contents={};self.closed=False;self.spans=[]

    def submit(self,identity,row):
        if self.closed or not 1<=identity<=MAX_JOBS or identity in self.jobs:raise ValueError('Preparation job identity/state')
        # Coordinator queues at most64 tiny row descriptors,not64 decoded meshes.
        if len(self.jobs)>=MAX_JOBS:raise ValueError('Preparation catalog capacity')
        self.jobs[identity]=dict(id=identity,row=list(row),phase='identify_wait',future=None,
                                discovered_ns=time.perf_counter_ns())

    def _run(self,phase,identity,call,*args):
        begin=time.perf_counter_ns();thread=threading.get_ident()
        try:return dict(value=call(*args),phase=phase,id=identity,begin_ns=begin,end_ns=time.perf_counter_ns(),thread=thread)
        except Exception as exc:
            return dict(error=str(exc),phase=phase,id=identity,begin_ns=begin,end_ns=time.perf_counter_ns(),thread=thread)

    def pump(self):
        if self.closed:return []
        completed=[]
        for job in list(self.jobs.values()):
            future=job['future']
            if future is None or not future.done():continue
            # Stable first-observed canonical identity,even if duplicate hashes
            # finish out of order. This orders tiny result commits,not conversion.
            if job['phase']=='identify' and any(j['id']<job['id'] and j['phase'] in ('identify_wait','identify') for j in self.jobs.values()):continue
            result=future.result();job['future']=None
            self.spans.append({k:v for k,v in result.items() if k!='value'})
            if 'error' in result:job.update(phase='failed',error=result['error']);job.pop('mesh',None);completed.append(job);continue
            if job['phase']=='identify':
                signature,mesh=result['value'];job['signature']=signature
                canonical=self.contents.get(signature)
                if canonical is not None:
                    job.update(phase='alias',canonical=canonical) # Discard duplicate decoded mesh.
                else:
                    self.contents[signature]=job['id'];job.update(phase='prepare_wait',mesh=mesh)
            else:
                job.update(phase='ready',prepared=result['value']);job.pop('mesh',None);completed.append(job)
        # Prepare already-decoded assets before admitting more large decoded data.
        active=sum(j['future'] is not None for j in self.jobs.values())
        for phase in ('prepare_wait','identify_wait'):
            for job in self.jobs.values():
                if active>=self.workers:break
                if job['phase']!=phase:continue
                if phase=='identify_wait':call,args=self.identify,(job['row'],)
                else:call,args=self.prepare,(job['row'],job['mesh'],job['id'])
                job['phase']='identify' if phase=='identify_wait' else 'prepare'
                job['future']=self.executor.submit(self._run,job['phase'],job['id'],call,*args);active+=1
        return completed

    def settled(self,identities):
        def done(identity):
            job=self.jobs[identity]
            if job['phase']=='alias':return done(job['canonical'])
            return job['phase'] in ('ready','failed')
        return all(done(i) for i in identities)

    def close(self):
        if self.closed:return
        self.closed=True
        self.executor.shutdown(wait=True,cancel_futures=True)

    def report(self):
        intervals=sorted((s[k],delta) for s in self.spans if s['phase']=='prepare'
                         for k,delta in (('begin_ns',1),('end_ns',-1)))
        active=peak=0
        for _,delta in intervals:active+=delta;peak=max(peak,active)
        return dict(workers=self.workers,jobs=len(self.jobs),peak_parallel_preparations=peak,clock='QueryPerformanceCounter via perf_counter_ns',
                    spans=self.spans,closed=self.closed,
                    jobs_summary=[dict(id=j['id'],owner=j['row'][1] if len(j['row'])>1 else j['row'][0],
                        discovered_ns=j['discovered_ns'],phase=j['phase'],canonical=j.get('canonical',j['id'])) for j in self.jobs.values()],
                    unfinished=[j['id'] for j in self.jobs.values() if j['phase'] not in ('ready','failed','alias')])
