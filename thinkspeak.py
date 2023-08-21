import requests
import pandas as pd
import streamlit as st
import plotly.express as px


THINGSPK_CHANNEL_ID = '2246162'
THINGSPK_API_READ_KEY = 'W5552EETGI8TGQJW'
URL = f'https://api.thingspeak.com/channels/{THINGSPK_CHANNEL_ID}/feeds.json?api_key={THINGSPK_API_READ_KEY}'
#https://api.thingspeak.com/channels/2246162/feeds.json?api_key=W5552EETGI8TGQJW
response = requests.get(URL)
data = response.json()

df = pd.DataFrame(data['feeds'])
df = df.astype({'field1':'float'})
df = df.astype({'field2':'float'})

st.write(df)  # Display raw data
st.write(df.info())
# Or visualize using plotly or any other visualization library
fig1 = px.line(df, x="created_at", y="field1", title='Temperature', markers=True)  # Assuming field1 is temperature
fig2 = px.line(df, x="created_at", y="field2", title='PH', markers=True)  # Assuming field1 is temperature
st.plotly_chart(fig1, use_container_width=True)
st.plotly_chart(fig2, use_container_width=True)





avg_temperature = df['field1'].mean()
min_temperature = df['field1'].min()
max_temperature = df['field1'].max()

avg_pH = df['field2'].mean()
min_pH = df['field2'].min()
max_pH = df['field2'].max()


