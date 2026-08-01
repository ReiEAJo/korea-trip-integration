
import streamlit as st
import plotly.express as px
import pandas as pd
from streamlit_plotly_events import plotly_events

st.title('Plotly Events Test')
df = pd.DataFrame({'region': ['A', 'B', 'C'], 'val': [10, 20, 30]})
fig = px.treemap(df, path=[px.Constant('all'), 'region'], values='val')

selected_points = plotly_events(fig, click_event=True, hover_event=False)
st.write('Selected:', selected_points)
