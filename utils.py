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



def colorize_df(df, vmin, vmax):
    # df = df.style.background_gradient(cmap=cmap_coolwarm, vmin=0, vmax=90)
    def f(val):
        val = 45 if val > 45 else val
        idx = int((val-vmin)/(vmax-vmin)*(len(colorlist_coolwarm)-1))
        if idx >= len(colorlist_coolwarm) or idx < 0:
            print(idx)
        color = colorlist_coolwarm[idx]
        return 'background-color: %s' % color
    df = df.style.applymap(f)
    df = df.format('{:.3g}')
    
    return df

def get_sesstion_id():
    if version.parse(st.__version__) < version.parse("1.4"):
        from streamlit.report_thread import get_report_ctx
        ctx = get_report_ctx()
        return ctx.session_id
    else:
        from streamlit.runtime.scriptrunner.script_run_context import get_script_run_ctx
        ctx = get_script_run_ctx()
        return ctx.session_id

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