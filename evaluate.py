import streamlit as st
import numpy as np
from glob import glob
import os
import shutil
from skimage import io, img_as_bool
import pandas as pd
import scipy.io as scio
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.font_manager import FontProperties
import cv2
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
        
        for i_s, s in list(enumerate(self.shape_names)):

            path = os.path.join(dataset_dir, '{}_{}'.format(s, self.texture_names[0]),'Normal_gt.mat')
            gt = scio.loadmat(path)['Normal_gt']
            
            for i_t, t in enumerate(self.texture_names):
                self.progress_bar.progress((i_s * self.nt + i_t) / self.num_tot_objs)
                
                path = os.path.join(dataset_dir, '{}_{}'.format(s, self.texture_names[0]),'mask.png')
                mask = io.imread(path)
                
                # TODO: support other format
                path = os.path.join(self.est_dir ,'{}_{}.mat'.format(s,t))
                nest = read_nest(path)
                h, w = nest.shape[:2]
                if (h, w) != (1001, 1001):
                    gt = cv2.resize(gt, (h, w), interpolation=cv2.INTER_NEAREST)
                    mask = cv2.resize(mask, (h, w), interpolation=cv2.INTER_NEAREST)
                    if i_s == 0 and i_t == 0:
                        st.write(f"[WARN] Resizing GT normal from (1001, 1001) into ({h}, {w}) with nearest neighbor interpolation")

                mask = img_as_bool(mask)
                ang_err = np.arccos((gt * nest).sum(-1).clip(-1,1)) / np.pi * 180
                    
                cut = ang_err.copy()
                ang_err = ang_err[mask]
                df_mean.iloc[i_s, i_t] = ang_err.mean()
                
                ## Save emap
                # cut[cut > 45] = 45
                # cut[np.logical_not(mask_)] = 0
                # fig = plt.figure(figsize=(5,5))
                # plt.imshow(cut, cmap='RdYlGn_r', vmin=0, vmax=45)
                # plt.axis('off')
                # fig.savefig(os.path.join(self.errmap_dir, '{}_{}.png'.format(s, t)), bbox_inches='tight')
                # plt.close('all')
                    
        df_mean.to_csv(os.path.join(self.result_dir, 'mean.csv'))
        avg_mae = df_mean.to_numpy().astype('float64').mean()
        if avg_mae > 13:
            shutil.rmtree(self.est_dir)  ## delete bad results
        return df_mean
