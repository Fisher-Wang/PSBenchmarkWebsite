import streamlit as st
import io
import zipfile
import os
import json
import pandas as pd
import numpy as np
from config import data_dir, default_shape_shownames, default_texture_shownames, est_dir_name
from database import DashboardDB
from evaluate import Evaluate
from utils import get_sesstion_id, colorize_df
from draw import plot
import gc
from typing import Type

def clear_cache():
    st.caching.clear_memo_cache()
    st.caching.clear_singleton_cache()
    st.legacy_caching.clear_cache()
    gc.collect()

class MainPage():
    def __init__(self):
        gc.collect()
        self.username = None
        self.session_id = get_sesstion_id()
        
        self.shapes = default_shape_shownames[:]
        self.textures = default_texture_shownames[:]
        
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
                data = account_db.fetch_account(username, password)
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
            if uncompressed_size > (1<<30):
                st.write('[ERROR] Fail in extraction: unscompressed size exceeds 1GB!')
                return False
            st.write('[INFO] Successfully convert to zip file')
            zf.extractall(os.path.join(self.user_dir, est_dir_name))
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

    def evaluate(self):
        progress_bar = st.progress(0.0)
        eval = Evaluate(self.user_dir, self.shapes, self.textures, progress_bar=progress_bar)
        self.df_mean = eval.evaluate()
        progress_bar.progress(1.0)
        self.score = self.df_mean.to_numpy().mean()
        return True
    
    def show_evaluate_result(self):
        df_mean = colorize_df(self.df_mean, 0, 45)
        st.subheader("Result")
        st.dataframe(df_mean)
    
    def record_score(self, dashboard_db, score):
        dashboard_db.update_record(self.username, self.session_id, score)
    
    def download_pdf_report(self):
        fig = plot(self.df_mean, self.shapes, self.textures)
        path = os.path.join(self.user_dir, 'result.pdf')
        fig.savefig(path, dpi=300, bbox_inches='tight')
        with open(path, 'rb') as f:
            st.download_button('Download PDF Report', f, file_name=f'{self.username}_report.pdf')

    def download_csv_report(self):
        array = self.df_mean.to_numpy().astype('float')
        # array = np.round(array, 2)
        df = pd.DataFrame(array, index=default_shape_shownames, columns=default_texture_shownames)
        path = os.path.join(self.user_dir, 'result.csv')
        df.to_csv(path)
        with open(path, 'rb') as f:
            st.download_button('Download CSV Report', f, file_name=f'{self.username}_report.csv')

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
            self.user_dir = os.path.join(data_dir, f'{username}_{self.session_id}')
            st.success(f"Successfully logged in as {username}, welcome!")
            st.markdown('### Submit Your Estimated Normal Map')
            st.markdown('##### Submission File Structure')
            st.markdown("1. The normal map of all the 100 objects should be included in the zip file, each named as '{shape}_{material}.mat' , where the shapes and materials are: ")
            st.markdown('''
                ```text
                shapes: BALL, GOLF, SPIKE, NUT, SQUARE, PENTAGON, HEXAGON, PROPELLER, TURBINE, BUNNY
                materials: POM, PP, NYLON, PVC, ABS, BAKELITE, Al, Cu, STEEL, ACRYLIC
                ```
            ''')
            st.markdown("2. In the mat file, the key-value structure should be {'Normal_est': normal_map}.")
            st.markdown("")
            st.markdown('''
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
                ```''')
            with open('data/CNN-PS_0.25.zip', 'rb') as f:
                st.download_button('Download Example Submission File', f, file_name='example.zip', mime='application/zip')
            st.markdown('4. **Normal Map Size**. Note that the estimated normal map in the example is downsampled in the degree of 1/4, with the total size of only 27MB, and the resolution is only 250x250. <u>**However, we recommand that you submit your normal map in full resolution 1001x1001 to get the most precise evaluation result**</u>. If your normal map shape is not 1001x1001, we will resize the GT normal into your shape with nearest neighbor interpolation before evaluation. If you submit the full resolution version, the file size should be around 900MB, and it may take a few minutes to upload and evaluate. ', unsafe_allow_html=True)
            st.markdown('5. **Data Range**. Your normal map data should be in range [-1, 1]. ')
            st.markdown('##### Upload Your Normal Map Zip Archive')
            if self.uploadfile():
                clear_cache()
                if self.evaluate():
                    clear_cache()
                    self.record_score(dashboard_db, self.score)
                    self.show_evaluate_result()
                    clear_cache()
                    ## TODO: delete following test code
                    # st.write(dashboard_db.view_all_records())
                    
                    self.download_pdf_report()
                    self.download_csv_report()
        self.showtable(dashboard_db)
        # st.write("Your can give a name to your method:")
        # method_name = st.text_input('Method Name', value='')
        # if st.button('Set'):
        #     pass

        clear_cache()
