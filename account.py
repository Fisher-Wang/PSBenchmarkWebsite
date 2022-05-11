import streamlit as st
import io
import zipfile
import os
import json
import pandas as pd
import numpy as np
from config import data_dir, default_shape_shownames, default_texture_shownames, est_dir_name
from evaluate import Evaluate
from utils import get_sesstion_id, colorize_df
from draw import plot
import gc

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
        st.write("Don't have an account? Please sign up.")
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
            st.write('successfully get bytes')
            zf = zipfile.ZipFile(io.BytesIO(bytes), "r")
            st.write('successfully convert to zip file')
            zf.extractall(os.path.join(self.user_dir, est_dir_name))
            # st.write(f'successfully write to folder {self.user_dir}/{est_dir_name}')
            st.write('successfully write to folder')
            return True
            
    def showtable(self, db):
        st.subheader('Ranking')
        data = db.fetch_records_for_show()
        df = pd.DataFrame(data, columns=['User Name', 'Last Submission Time', 'Mean Angular Error'])
        df.columns.name = 'Rank'
        st.dataframe(df, 1600, 400)

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

    def login(self, account_db, dashboard_db):
        gc.collect()
        logged = 0
        first_entry = 0  # XXX: 加上first_entry的判断能够优化显示效果，但是我不知道为什么，streamlit背后的原理十分玄学……
        login_section_ph = st.empty()
        login_section_ph.subheader("Login Section")
        st.write('To evaluate your own algorithm, you may sign in to provide a user name.')
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
            logged = 1
            login_section_ph.empty()
            username_ph.empty()
            password_ph.empty()
            button_ph.empty()
            self.username = username
            self.user_dir = os.path.join(data_dir, f'{username}_{self.session_id}')
            st.subheader('Evaluation Section')
            st.success(f"Successfully logged in as {username}, welcome!")
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
        if not logged:
            self.signup(account_db)
        self.showtable(dashboard_db)
        clear_cache()
