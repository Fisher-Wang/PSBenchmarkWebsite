from colors import colorlist_coolwarm
import streamlit as st
import os
from os.path import join as pjoin
from os.path import exists as pexists
import shutil
from skimage import io, img_as_bool
import scipy.io as scio
from packaging import version
import numpy as np
from streamlit import runtime
if version.parse(st.__version__) < version.parse("1.4"):
    from streamlit.report_thread import get_report_ctx as get_script_run_ctx
else:
    from streamlit.runtime.scriptrunner.script_run_context import get_script_run_ctx


def colorize_df(df, vmin, vmax):
    # df = df.style.background_gradient(cmap=cmap_coolwarm, vmin=0, vmax=90)
    def f(val):
        val = vmax if val > vmax else val
        idx = int((val-vmin)/(vmax-vmin)*(len(colorlist_coolwarm)-1))
        color = colorlist_coolwarm[idx]
        return 'background-color: %s' % color
    df = df.style.map(f)
    df = df.format('{:.3g}')
    
    return df

def get_sesstion_id():
    ctx = get_script_run_ctx()
    return ctx.session_id

def get_remote_ip() -> str:
    """Get remote ip."""
    ## ref: https://stackoverflow.com/a/75437429
    try:
        ctx = get_script_run_ctx()
        if ctx is None:
            return None

        session_info = runtime.get_instance().get_client(ctx.session_id)
        if session_info is None:
            return None
    except Exception as e:
        return None

    return session_info.request.remote_ip

def read_mat(path):
    nest = scio.loadmat(path)
    nest = nest[list(nest.keys())[-1]]
    return nest

def read_mask(path):
    mask = img_as_bool(io.imread(path))
    if len(mask.shape) == 3:
        mask = mask[..., 0]
    return mask

def get_emap(est, gt, mask):
    '''
    - return: `(emap, mae)`, in degree
    '''
    emap = np.arccos((est * gt).sum(-1).clip(-1, 1)) / np.pi * 180
    emap[~mask] = 0
    mae = np.nanmean(emap[mask])
    return emap, mae

def mkdir(path, delete_old=False):
    if delete_old and pexists(path):
        shutil.rmtree(path)
    os.makedirs(path, exist_ok=True)
    return path