import streamlit as st
import streamlit.components.v1 as components
import numpy as np
import pandas as pd
from evaluate import Evaluate100
from config import ConfigPi

from database import AccountDB, DashboardDB
from account import MainPagePi
from utils import *

st.set_page_config(page_title='DiLiGenT-Pi Benchmark', page_icon=':fire', layout='centered')
st.title('DiLiGenT-$\\small \Pi$ Benchmark')
main_page = MainPagePi(ConfigPi)
account_database = AccountDB('data_pi.db')
dashboard_database = DashboardDB('data_pi.db')


choice = st.sidebar.selectbox('Menu', ['Login & Evaluate', 'Signup'])
st.sidebar.write('To evaluate your own algorithm, you may sign in to provide a user name.')
st.sidebar.write("Don't have an account? Switch to the Signup page and create an account!")
if choice == 'Login & Evaluate':
    main_page.login(account_database, dashboard_database)
elif choice == 'Signup':
    main_page.signup(account_database)
