from colors import colorlist_coolwarm
from streamlit.report_thread import get_report_ctx
import os
from os.path import join as pjoin
from config import default_shape_shownames, default_texture_shownames, est_dir_name
from skimage import io
import scipy.io as scio

def get_good_est_dir(usr_dir):
    d = os.path.join(usr_dir, est_dir_name)
    s0 = default_shape_shownames[0]
    t0 = default_texture_shownames[0]
    if os.path.exists(os.path.join(d, f'{s0}_{t0}.mat')):
        return d
    sub_dirs = [pjoin(d, x) for x in os.listdir(d) if os.path.isdir(pjoin(d, x))]
    for sd in sub_dirs:
        if os.path.exists(os.path.join(sd, f'{s0}_{t0}.mat')):
            return sd
    raise Exception('Bad File Structure!')

def read_nest(path):
    format = path.split('.')[-1].lower()
    if format == 'mat':
        est = scio.loadmat(path)
        key = list(est.keys())[3]
        est = est[key]
    elif format == 'png':
        est = io.imread(path)
        est = (est - 128) / 128
    else:
        raise ValueError
    return est

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
    ctx = get_report_ctx()
    return ctx.session_id