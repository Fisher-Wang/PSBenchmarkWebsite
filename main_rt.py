import streamlit as st
import streamlit.components.v1 as components
import numpy as np
import pandas as pd
from evaluate import Evaluate100
from config import ConfigRT

from database import AccountDB, DashboardDB
from account import MainPageRT
from utils import *

st.set_page_config(page_title='DiLiGenRT Benchmark', page_icon=':fire', layout='centered')
st.title('DiLiGenRT Benchmark')
main_page = MainPageRT(ConfigRT)
account_database = AccountDB('data_rt.db')
dashboard_database = DashboardDB('data_rt.db')


choice = st.sidebar.selectbox('Menu', ['Login & Evaluate', 'Signup'])
st.sidebar.write('To evaluate your own algorithm, you may sign in to provide a user name.')
st.sidebar.write("Don't have an account? Switch to the Signup page and create an account!")
if choice == 'Login & Evaluate':
    main_page.login(account_database, dashboard_database)
elif choice == 'Signup':
    main_page.signup(account_database)
