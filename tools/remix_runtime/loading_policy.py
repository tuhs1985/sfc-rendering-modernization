"""Offline-only experiments with pinned Remix's existing startup facilities.

No custom loader, changes to images/materials, or implicit gameplay preset.
The receipt describes supplied inputs, NOT a public runtime readiness query.
"""
KEYS=('DXVK_ASYNC_ASSET_LOADING','RTX_ASYNC_SHADER_PREWARMING',
      'RTX_ENABLE_ASYNC_COMPILATION','DXVK_WAIT_ASYNC_TEXTURES','DXVK_USE_RTXIO')
MODES=('inherit','async','blocking','rtxio')


def configure(mode,environment,*,offline):
    if mode not in MODES:raise ValueError('Unknown loading policy')
    if mode!='inherit' and not offline:raise ValueError('Loading experiment is offline only')
    before={key:environment.get(key) for key in KEYS}
    options={}
    if mode=='rtxio':
        options={'rtx.io.enabled':True,'rtx.io.useAsyncQueue':True}
        environment['DXVK_USE_RTXIO']='1'
    elif mode!='inherit':
        asynchronous=mode=='async'
        options={'rtx.initializer.asyncAssetLoading':asynchronous,
                 'rtx.initializer.asyncShaderPrewarming':True,
                 'rtx.initializer.asyncShaderFinalizing':asynchronous,
                 'rtx.shader.enableAsyncCompilation':asynchronous,
                 'rtx.alwaysWaitForAsyncTextures':False}
        for key,value in zip(KEYS,(asynchronous,True,asynchronous,False)):
            environment[key]='1' if value else '0'
    text=''.join(f'{key} = {str(value)}\n' for key,value in options.items())
    return text,dict(mode=mode,inherited_environment=before,
                     supplied_environment={key:environment.get(key) for key in KEYS},
                     supplied_config=options,
                     scope='Native renderer inputs;not a runtime completion/readiness receipt')
