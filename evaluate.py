import streamlit as st
import numpy as np
from os.path import join as pjoin
import shutil
import pandas as pd
import cv2
from utils import *
import itertools
from abc import ABC, abstractmethod
from config import ConfigBase


class EvaluateBase(ABC):
    def __init__(self, config, username, userdir, names) -> None:
        self.config = config
        self.username = username
        self.userdir = userdir
        self.result_dir = mkdir(pjoin(userdir, 'result'))
        self.names = names
        self.est_dir = self.get_good_est_dir(self.userdir)
        self.maes = []
        
        self.H = None
        self.W = None

    def evaluate(self):
        progress_bar = st.progress(0.0)
        for i, name in enumerate(self.names):
            progress_bar.progress(i / len(self.names))
            
            gt = read_mat(pjoin(self.config.dataset_dir, name, 'Normal_gt.mat'))
            mask = read_mask(pjoin(self.config.dataset_dir, name, 'mask.png')).astype('uint8')
            
            # TODO: support other format
            nest = read_mat(pjoin(self.est_dir, f'{name}.mat'))
            h, w = nest.shape[:2]
            if (h, w) != (self.H, self.W):
                gt = cv2.resize(gt, (h, w), interpolation=cv2.INTER_NEAREST)
                mask = cv2.resize(mask, (h, w), interpolation=cv2.INTER_NEAREST)
                # nest = cv2.resize(nest, (self.H, self.W), interpolation=cv2.INTER_NEAREST)
                if i == 0:
                    st.warning(f"[WARN] Resizing GT normal from ({self.H}, {self.W}) into ({h}, {w}) with nearest neighbor interpolation")

            mask = mask.astype(bool)
            _, mae = get_emap(nest, gt, mask)
            self.maes.append(mae)
        progress_bar.progress(1.0)
        
        avg = np.mean(self.maes)
        
        ## Remove uploaded data anyway
        shutil.rmtree(self.est_dir)
    
    @property
    def score(self):
        return np.array(self.maes).mean()
    
    def get_good_est_dir(self, usr_dir):
        d = os.path.join(usr_dir, ConfigBase.est_dir_name)
        if os.path.exists(os.path.join(d, f'{self.names[0]}.mat')):
            return d
        sub_dirs = [pjoin(d, x) for x in os.listdir(d) if os.path.isdir(pjoin(d, x))]
        for sd in sub_dirs:
            if os.path.exists(os.path.join(sd, f'{self.names[0]}.mat')):
                return sd
        raise Exception('Bad File Structure!')
    
class Evaluate100(EvaluateBase):
    def __init__(self, config, username, userdir, shape_names, texture_names) -> None:
        self.shape_names = shape_names 
        self.texture_names = texture_names 
        names = [f'{s}_{t}' for s, t in itertools.product(self.shape_names, self.texture_names)]
        super().__init__(config, username, userdir, names)
        
        self.H = 1001
        self.W = 1001

    def show_result(self):
        df = pd.DataFrame(np.array(self.maes).reshape(len(self.shape_names), len(self.texture_names)), index=self.shape_names, columns=self.texture_names)
        
        ## HTML Table showing in website
        df_show = colorize_df(df, 0, 45)
        st.subheader("Result")
        st.dataframe(df_show)
        
        ## PDF Table for download
        from draw import plot
        fig = plot(df, self.shape_names, self.texture_names)
        path = pjoin(self.userdir, 'result.pdf')
        fig.savefig(path, dpi=300, bbox_inches='tight')
        with open(path, 'rb') as f:
            st.download_button('Download PDF Report', f, file_name=f'{self.username}_report.pdf')
        
        ## CSV Table for download
        path = pjoin(self.result_dir, 'result.csv')
        df.to_csv(path)
        with open(path, 'rb') as f:
            st.download_button('Download CSV Report', f, file_name=f'{self.username}_report.csv')

class EvaluatePi(EvaluateBase):
    def __init__(self, config, username, userdir, shape_names, texture_names) -> None:
        self.shape_names = shape_names 
        self.texture_names = texture_names 
        names = self.shape_names
        super().__init__(config, username, userdir, names)
        
        self.H = 1216
        self.W = 1216

    def show_result(self):
        df = pd.DataFrame(np.array(self.maes).reshape(len(self.shape_names), len(self.texture_names)), index=self.shape_names, columns=self.texture_names)
        
        ## HTML Table showing in website
        df_show = colorize_df(df, 0, 30)
        st.subheader("Result")
        st.dataframe(df_show)
        
        ## CSV Table for download
        path = pjoin(self.result_dir, 'result.csv')
        df.to_csv(path)
        with open(path, 'rb') as f:
            st.download_button('Download CSV Report', f, file_name=f'{self.username}_report.csv')

class EvaluateRT(EvaluateBase):
    def __init__(self, config, username, userdir, shape_names, texture_names) -> None:
        self.shape_names = shape_names 
        self.texture_names = texture_names 
        names = self.shape_names
        super().__init__(config, username, userdir, names)
        
        self.H = 960
        self.W = 960

    def show_result(self):
        df = pd.DataFrame(np.array(self.maes).reshape(len(self.shape_names), len(self.texture_names)), index=self.shape_names, columns=self.texture_names)
        
        ## HTML Table showing in website
        df_show = colorize_df(df, 0, 30)
        st.subheader("Result")
        st.dataframe(df_show)
        
        ## CSV Table for download
        path = pjoin(self.result_dir, 'result.csv')
        df.to_csv(path)
        with open(path, 'rb') as f:
            st.download_button('Download CSV Report', f, file_name=f'{self.username}_report.csv')
