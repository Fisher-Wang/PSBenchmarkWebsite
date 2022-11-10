import streamlit as st
import numpy as np
from glob import glob
import os
from skimage import io, img_as_bool
import pandas as pd
import scipy.io as scio
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.font_manager import FontProperties
from skimage.transform import resize
from utils import get_good_est_dir, read_nest

from config_dataset import dataset_dir
from config import show, est_dir_name

class Evaluate():
    def __init__(self, user_dir, shape_names, texture_names, progress_bar) -> None:
        self.user_dir = user_dir
        self.est_dir = get_good_est_dir(self.user_dir)
        
        self.shape_names = shape_names 
        self.texture_names = texture_names 
        self.progress_bar = progress_bar
        
        self.shape_shownames = shape_names
        self.texture_shownames = texture_names
        self.errmap_dir = os.path.join(user_dir, 'errmap')
        self.result_dir = os.path.join(user_dir, 'result')
        
        # for the progress bar
        self.ns = len(shape_names)
        self.nt = len(texture_names)
        self.num_tot_objs = self.ns * self.nt
        
        os.makedirs(self.errmap_dir, exist_ok=True)
        os.makedirs(self.result_dir, exist_ok=True)
        
    def evaluate(self):
        
        df_mean = pd.DataFrame(index=self.shape_shownames, columns=self.texture_shownames)
        df_var = pd.DataFrame(index=self.shape_shownames, columns=self.texture_shownames)
        df_mid = pd.DataFrame(index=self.shape_shownames, columns=self.texture_shownames)
        
        for i_s, s in list(enumerate(self.shape_names)):
            # self.progress_bar.progress((i_m * self.ns + i_s) / (self.nm * self.ns))
            
            path = os.path.join(dataset_dir, '{}_{}'.format(s, self.texture_names[0]),'Normal_gt.mat')
            gt = scio.loadmat(path)['Normal_gt']
            
            path = os.path.join(dataset_dir, '{}_{}'.format(s, self.texture_names[0]),'mask.png')
            mask = img_as_bool(io.imread(path))

            for i_t, t in enumerate(self.texture_names):
                self.progress_bar.progress((i_s * self.nt + i_t) / self.num_tot_objs)
                
                ## .mat version
                # path = os.path.join(args.est_dir, '{}/{}_{}.mat'.format(m, o, t))
                # est = scio.loadmat(path)
                # if 'Normal_est' in est.keys():
                #     est = est['Normal_est']
                # else:
                #     est = est['normal']
                
                ## .png version
                # TODO: judge which format to deal with
                path = os.path.join(self.est_dir ,'{}_{}.mat'.format(s,t))
                nest = read_nest(path)
                h, w = nest.shape[:2]
                if (h, w) != (1001, 1001):
                    gt = resize(gt, (h, w), order=0)
                    mask = resize(mask, (h, w), order=0)
                    if i_s == 0 and i_t == 0:
                        st.write(f"[WARN] Resizing GT normal from (1001, 1001) into ({h}, {w}) with nearest neighbor interpolation")

                ang_err = np.arccos((gt * nest).sum(-1).clip(-1,1)) / np.pi * 180
                if s == 'bunny':
                    ang_err = ang_err[::-1, ::-1]
                    
                cut = ang_err.copy()
                ang_err = ang_err[mask]
                df_mean.iloc[i_s, i_t] = ang_err.mean()
                df_var.iloc[i_s, i_t] = ang_err.var()
                df_mid.iloc[i_s, i_t] = np.median(ang_err)
                
                ## Save emap
                # cut[cut > 45] = 45
                # cut[np.logical_not(mask_)] = 0
                # fig = plt.figure(figsize=(5,5))
                # plt.imshow(cut, cmap='RdYlGn_r', vmin=0, vmax=45)
                # plt.axis('off')
                # fig.savefig(os.path.join(self.errmap_dir, '{}_{}.png'.format(s, t)), bbox_inches='tight')
                # plt.close('all')
                    
        df_mean.to_csv(os.path.join(self.result_dir, 'mean.csv'))
        df_var.to_csv(os.path.join(self.result_dir, 'var.csv'))
        df_mid.to_csv(os.path.join(self.result_dir, 'mid.csv'))
        return df_mean
