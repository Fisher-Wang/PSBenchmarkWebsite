import streamlit as st
import streamlit.components.v1 as components
import numpy as np
import pandas as pd
from evaluate import Evaluate

from database import AccountDB, DashboardDB
from account import MainPage
from utils import *



# def evaluation():
#     methods = [d for d in os.listdir(user_dir) if os.path.isdir(os.path.join(user_dir, d)) and d in default_methods]
#     shapes = default_shapes[:]
#     textures = default_textures[:]
    
#     progress_bar = st.progress(0.0)
#     eval = Evaluate(user_dir, methods, shapes, textures, show_errmap=True, progress_bar=progress_bar)
#     eval.evaluate()
#     progress_bar.progress(1.0)

#     print('done!')


st.set_page_config(page_title='DiLiGenT10^2 Benchmark', page_icon=':fire', layout='centered')
st.title('DiLiGenT10^2 Benchmark')
main_page = MainPage()
account_database = AccountDB()
dashboard_database = DashboardDB()

main_page.login(account_database, dashboard_database)
# choice = st.sidebar.selectbox('Evaluation-Menu', ['Login', 'Signup', 'About','Ranking'])
# st.sidebar.write('To evaluate your own algorithm, you may sign in to provide a user name.')
# if choice == 'Login':
#     account.login(account_database, dashboard_database)

# elif choice == 'Signup':
#     account.signup(account_database)
        
# elif choice == 'About':
#     st.write('authors')
# elif choice == 'Ranking':
#     account.showtable(dashboard_database)


        