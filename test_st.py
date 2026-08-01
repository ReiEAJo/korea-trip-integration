
import streamlit as st
import plotly.express as px
import pandas as pd
df = pd.DataFrame({'region': ['A', 'B', 'C'], 'val': [10, 20, 30]})
fig = px.treemap(df, path=[px.Constant('all'), 'region'], values='val')
event = st.plotly_chart(fig, on_select='rerun')
st.write(event)
