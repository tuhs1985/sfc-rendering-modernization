"""Opt-in candidate1.6.1 checkout; normal runtime selection is untouched.

Uses supported USD materials, existing flat publisher, and ordinary D3D9 meshes.
No renderer SDK geometry submission or new asset loader.
"""
import time
import json
import struct

from progressive_scene_relay import Relay as Progressive


def configure_child(backend,environment):
    if not backend or backend.get('release')!='1.6.1':
        raise ValueError('Verified async material checkout backend required')
    before=environment.get('DXVK_ASYNC_ASSET_LOADING')
    environment['DXVK_ASYNC_ASSET_LOADING']='1'
    # Exercise the existing private renderer startup once. Its completion precedes
    # renderer-ready.bin; afterward warm_start waits without further Presents.
    environment['SFC_D3D9_RENDER_PREWARM']='triangle'
    environment['SFC_D3D9_STARTUP_PROFILE']='1'
    return ('rtx.initializer.asyncAssetLoading = True\n'
            'rtx.enableReplacementAssets = True\n'),dict(
        release='1.6.1',material_library='flat',complete_asset_stages=True,
        initial_material_priming=True,private_render_prewarm='triangle',
        supplied_async_asset_loading='1',inherited_async_asset_loading=before,
        host_sha256=backend['host_sha256'],runtime_sha256=backend['runtime_sha256'],
        header_sha256=backend['header_sha256'],scope='Explicit checkout child only;normal1.5.2 unchanged')


def backend_inputs():
    from runtime_candidate import verify,digest
    candidate=verify(require_host=True)
    return dict(release='1.6.1',exe=candidate['exe'],runtime=candidate['runtime'],
        host_sha256=digest(candidate['exe']),runtime_sha256=digest(candidate['runtime']),
        header_sha256=candidate['manifest']['header_sha256'],
        source_commit=candidate['manifest']['source_commit'],
        source_parity='Packaged5a7eec84/public0a6cd5b not instruction-level verified')


def receipt(backend):
    return {k:str(v) if k in ('exe','runtime') else v for k,v in backend.items()}


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
                path=self.folder/'gpu/renderer-ready.bin'
                try:raw=path.read_bytes()
                except FileNotFoundError:return
                if len(raw)<16:return  # Native writer has not finished yet.
                if len(raw)!=16:raise ValueError('Material priming readiness length')
                qpc,pid=struct.unpack('<2Q',raw)
                if not qpc or not 0<pid<=0xffffffff:raise ValueError('Material priming readiness identity')
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
        result=super().finish(pid)
        result['multi_scene']['async_material_checkout']=dict(
            backend=receipt(self.renderer_backend),material_library='flat',
            complete_asset_stages=True,finished_ns=time.perf_counter_ns(),
            material_priming=self.material_prime_ready)
        (self.folder/'live-owner.analysis.json').write_text(json.dumps(result,indent=2))
        return result

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
