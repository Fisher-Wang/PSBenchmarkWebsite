import streamlit as st
import io
import zipfile
import os
import json
import pandas as pd
import numpy as np
from database import DashboardDB
from evaluate import Evaluate100, EvaluatePi
from utils import get_sesstion_id, colorize_df
from draw import plot
import gc
from typing import Type
from packaging import version
from abc import ABC, abstractmethod
from os.path import join as pjoin

def clear_cache():
    if version.parse(st.__version__) < version.parse("1.4"):
        st.caching.clear_memo_cache()
        st.caching.clear_singleton_cache()
        st.legacy_caching.clear_cache()
    elif version.parse(st.__version__) < version.parse("1.18"):
        st.experimental_memo.clear()
        st.experimental_singleton.clear()
    else:
        st.cache_data.clear()
        st.cache_resource.clear()
    gc.collect()

class MainPageBase(ABC):
    def __init__(self, config):
        self.config = config
        self.shapes = self.config.shape_names
        self.textures = self.config.texture_names
        self.username = None
        self.session_id = get_sesstion_id()
        
    def signup(self, account_db):
        gc.collect()
        st.subheader("Create New Account")
        # st.write("Don't have an account? Please sign up.")
        username = st.text_input("User Name")
        password = st.text_input("Password", type='password')
        if st.button("Sign Up"):
            if not username:
                st.error('Empty user name. Try again!')
            else:
                data = account_db.fetch_account_by_username(username)
                print(data)
                if data:
                    st.error(f'Username {username} has been used. Try another one!')
                else:
                    account_db.add_account(username, password)
                    st.success(f"Sign up successfully.")
                    
    def uploadfile(self):
        file = st.file_uploader('choose a zip archive', ['zip'])
        if file is not None:
            bytes = file.getvalue()
            st.write('[INFO] Successfully get bytes')
            zf = zipfile.ZipFile(io.BytesIO(bytes), "r")
            uncompressed_size = sum([e.file_size for e in zf.infolist()])
            if uncompressed_size > 1.5 * (1<<30):
                st.write('[ERROR] Fail in extraction: uncompressed size exceeds 1.5GB!')
                return False
            st.write('[INFO] Successfully convert to zip file')
            zf.extractall(pjoin(self.user_dir, self.config.est_dir_name))
            st.write('[INFO] Successfully write to folder')
            return True
            
    def showtable(self, db: Type[DashboardDB]):
        st.subheader('Ranking')
        username_term = 'User Name'
        mae_term = 'Best MAE (Mean Angular Error)'
        submit_time_term = 'Submission Time'
        method_name_term = 'Method Name'
        last_mae_term = 'Last MAE'
        last_submit_term = 'Last Submission'

        data = db.fetch_records_for_show()
        df = pd.DataFrame(data, columns=[username_term, submit_time_term, mae_term, method_name_term])
        order = [0, 2, 1, 3]
        df = df[[df.columns[i] for i in order]]  # Reorder Columns

        data = db.fetch_last_submission()
        df_time = pd.DataFrame(data, columns=[username_term, last_mae_term, last_submit_term])

        df = pd.merge(df, df_time, on=username_term)
        df = df.drop(columns=[method_name_term])  # TODO: add method name later
        
        df.columns.name = 'Rank'
        # Ref: Convert string to float, https://stackoverflow.com/a/16729635/13874470
        df[mae_term] = df[mae_term].astype('float')
        df[last_mae_term] = df[last_mae_term].astype('float')
        # Ref: Set float precision, https://stackoverflow.com/a/62166854/13874470
        style = df.style.format({mae_term: '{:.2f}', last_mae_term: '{:.2f}'})  

        ## set table style
        ## Ref: color orange hex, https://www.color-hex.com/color/ffa500
        style = style.set_table_styles([
            {
                'selector': 'th',  # headers
                'props': [
                    # ('font-size', '30pt'), 
                    ('font-weight', 'bold'), 
                    ('background-color', '#FFB732')
                ]
            },
            {
                'selector': 'td',  # cells
                'props': [
                    # ('font-size', '30pt'), 
                    # ('font-weight', 'bold'), 
                    ('background-color', '#FFF6E5')
                ]
            }
        ])

        ## Option 1: Show Dataframe
        # st.dataframe(style.data, 1600, 400)

        ## Option 2: Show HTML Table
        html = style.to_html()
        ## align the table
        target = '<table '
        i = html.find(target) + len(target)
        html = html[:i] + 'style="margin: 0px auto;" ' + html[i:]
        st.markdown(html, unsafe_allow_html=True)

    def record_score(self, dashboard_db, score):
        dashboard_db.update_record(self.username, self.session_id, score)
    
    def login(self, account_db, dashboard_db):
        gc.collect()
        first_entry = 0  # XXX: 加上first_entry的判断能够优化显示效果，但是我不知道为什么，streamlit背后的原理十分玄学……
        login_section_ph = st.empty()
        login_section_ph.subheader("Login")
        username_ph = st.empty()
        password_ph = st.empty()
        button_ph = st.empty()
        username = username_ph.text_input("User Name ")
        password = password_ph.text_input("Password ", type='password')
        button_ph.button('Log In')
        data = account_db.fetch_account(username, password)
        if not data:
            if username != '' and not first_entry:
                st.warning("Incorrect username/password. Try again!")
            first_entry = 0
        else:
            login_section_ph.empty()
            username_ph.empty()
            password_ph.empty()
            button_ph.empty()
            self.username = username
            self.user_dir = pjoin(self.config.data_dir, f'{username}_{self.session_id}')
            st.success(f"Successfully logged in as {username}, welcome!")
            
            self.submission_description()
            
            st.markdown('##### Upload Your Normal Map Zip Archive')
            if self.uploadfile():
                clear_cache()
                Eval = Evaluate100 if self.config.type == '100' else EvaluatePi
                eval = Eval(self.config, self.username, self.user_dir, self.shapes, self.textures)
                eval.evaluate()
                self.record_score(dashboard_db, eval.score)
                eval.show_result()
        self.showtable(dashboard_db)
        # st.write("Your can give a name to your method:")
        # method_name = st.text_input('Method Name', value='')
        # if st.button('Set'):
        #     pass

        clear_cache()
        
    @abstractmethod
    def submission_description(self):
        pass

class MainPage100(MainPageBase):
    def __init__(self, config) -> None:
        super().__init__(config)
    
    def submission_description(self):
        st.markdown('''
            ### Submit Your Estimated Normal Map
            ##### Submission File Structure
            1. The normal map of all the 100 objects should be included in the zip file, each named as '{shape}_{material}.mat' , where the shapes and materials are: 
            ```text
            shapes: BALL, GOLF, SPIKE, NUT, SQUARE, PENTAGON, HEXAGON, PROPELLER, TURBINE, BUNNY
            materials: POM, PP, NYLON, PVC, ABS, BAKELITE, Al, Cu, STEEL, ACRYLIC
            ```
            2. In the mat file, the key-value structure should be {'Normal_est': normal_map}.
            3. The file structure diagram, along with a example submission file, are shown below for your reference. 
            ```text
            xxx.zip
            |__ BALL_POM.mat
            |__ BALL_PP.mat
            |__ ...
            |__ BALL_ACRYLIC.mat
            ...
            |__ BUNNY_POM.mat
            |__ BUNNY_PP.mat
            |__ ...
            |__ BUNNY_ACRYLIC.mat
            ```
            ''')
        with open('data/CNN-PS_0.25.zip', 'rb') as f:
            st.download_button('Download Example Submission File', f, file_name='example.zip', mime='application/zip')
        st.markdown('''
            4. **Normal Map Size**. Note that the estimated normal map in the example is downsampled in the degree of 1/4, with the total size of only 27MB, and the resolution is only 250x250. <u>**However, we recommand that you submit your normal map in full resolution 1001x1001 to get the most precise evaluation result**</u>. If your normal map shape is not 1001x1001, we will resize the GT normal into your shape with nearest neighbor interpolation before evaluation. If you submit the full resolution version, the file size should be around 900MB, and it may take a few minutes to upload and evaluate. 
            5. **Data Range**. Your normal map data should be in range [-1, 1]. 
            ''', unsafe_allow_html=True)

class MainPagePi(MainPageBase):
    def __init__(self, config) -> None:
        super().__init__(config)
    
    def submission_description(self):
        st.markdown(f'''
            ### Submit Your Estimated Normal Map
            ##### Submission File Structure
            1. The normal map of all the 30 objects should be included in the zip file, each named as '{{object}}.mat', where the object names are: 
            ```text
            {", ".join(self.shapes)}
            ```
            2. In the mat file, the key-value structure should be {{'Normal_est': normal_map}}.
            3. The file structure diagram, along with a example submission file, are shown below for your reference. 
            ```text
            xxx.zip
            |__ Flower.mat
            |__ Bird.mat
            |__ ...
            |__ Cloud-R.mat
            ```
            ''')
        with open('data/Pi_L2_0.25.zip', 'rb') as f:
            st.download_button('Download Example Submission File', f, file_name='example.zip', mime='application/zip')
        st.markdown('''
            4. **Normal Map Size**. Note that the estimated normal map in the example is downsampled in the degree of 1/4, with the total size of only 15MB, and the resolution is only 304x304. <u>**However, we recommand that you submit your normal map in full resolution 1216x1216 to get the most precise evaluation result**</u>. If your normal map shape is not 1216x1216, we will resize the GT normal into your shape with nearest neighbor interpolation before evaluation. If you submit the full resolution version, the file size should be around 250MB, and it may take a few minutes to upload and evaluate. 
            5. **Data Range**. Your normal map data should be in range [-1, 1]. 
            ''', unsafe_allow_html=True)