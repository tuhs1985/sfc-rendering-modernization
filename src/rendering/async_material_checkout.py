"""Opt-in candidate1.6.1 checkout; normal runtime selection is untouched.

Uses supported USD materials, existing flat publisher, and ordinary D3D9 meshes.
No renderer SDK geometry submission or new asset loader.
"""
import time
import json
import struct

from progressive_scene_relay import Relay as Progressive
from renderer_backend import backend_inputs, configure_child, receipt
from live_owner_timing import development_reports


class Relay(Progressive):
    def __init__(self,*args,**kwargs):
        backend=kwargs.pop('checkout_backend',None)
        if not backend or backend.get('release')!='1.6.1':raise ValueError('Explicit verified checkout backend required')
        kwargs['experimental_live_checkout']=True
        super().__init__(*args,**kwargs)
        self.async_material_checkout=True;self.renderer_backend=backend
        self.material_library='flat'
        self.material_prime_ready=None

    def commit_layers(self,initial):
        # This conversion belongs to the Remix/USD adapter, never canonical
        # captures, original images, plain D3D9 or future renderer adapters.
        from material_library import flat,publish_remix_revision
        root=self.folder/'gpu/rtx-remix/mods/sfc-policy'
        text,_=flat(root,self.layers,getattr(self,'tuning_overrides',None))
        revision=publish_remix_revision(root,text)
        self.material_events.append(dict(layers=len(self.layers),
            supervisor_monotonic_ns=time.perf_counter_ns(),clock='QueryPerformanceCounter',
            initial=initial,usd_revision=revision))

    def retry_publication(self):
        # Base catalog/movement delivery remains independent. Only enhancement
        # publication waits if it races the one-time renderer preparation.
        if self.pending_stage_ids or self.pending_library:
            if self.material_prime_ready is None:
                from warm_start import ready
                readiness=ready(self.receiver.channel)
                if readiness is None:return
                qpc,pid=readiness
                self.material_prime_ready=dict(qpc=qpc,host_pid=pid,observed_ns=time.perf_counter_ns(),
                    meaning='Private startup completed;not a per-material installation ACK')
        super().retry_publication()

    def flush_enhancements(self):
        # Base packets publish independently. Bound image IO to four groups per
        # cycle, but publish one complete enhanced stage per finished asset.
        processed=0
        while self.pending_enhancements and processed<4:
            kind,value=self.pending_enhancements[0]
            job=value if kind=='complete' else value[0]
            if not job.get('published'):break
            self.pending_enhancements.popleft()
            if job['phase']=='failed':continue
            if kind=='complete':
                expected={g[0] for g in job['manifest']['groups']}
                if set(self.material_pieces.get(job['id'],{}))!=expected:
                    raise ValueError('Completed material revision missing groups;retain base')
                self.pending_stage_ids.add(job['id']);self.pending_complete_ids.add(job['id'])
                continue
            _,piece=value
            try:self.accept_piece(job,piece)
            except (ValueError,OSError) as exc:self.fail_job(job,exc)
            processed+=1
        self.retry_publication()

    def finish(self,pid):
        return development_reports().finish_async_material_checkout(self,pid,super().finish)
    def poll(self,pid,from_service=False):
        super().poll(pid,from_service=from_service)
        # The coordinator is the only writer of the material library. Never
        # publish from the supervisor while its service owns the scene.
        if getattr(self,'live_tuning',False) and (not self.service or from_service):
            if not hasattr(self,'tuning_controls'):
                from d3d9_tuning import Controls
                self.tuning_controls=Controls(self)
            self.tuning_controls.poll()

    def stop(self):
        # Stop service callbacks before releasing the tuning worker/storage.
        if self.service:
            self.service.close()
            if self.service.error:self.error=str(self.service.error)
            self.service=None
        if hasattr(self,'tuning_controls'):
            self.tuning_controls.close();del self.tuning_controls
        super().stop()
