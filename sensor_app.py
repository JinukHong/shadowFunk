import streamlit as st
import pandas as pd
import numpy as np
import datetime
import collections
import openai
import requests
import plotly.express as px

openai.api_key = st.secrets["secrets"]['OPENAI_API_KEY']


st.title('Sein Farm in your hand')
tab1, tab2, tab3= st.tabs(['Tab A' , 'Tab B', 'Tab C'])

with tab1:
    st.header('About Sein Farm')


with tab2:
    st.write('Displaying dummy data for temperature and pH levels.')

    col1,col2 = st.columns([1,1])

    # Generate dummy data
    def generate_data():
        THINGSPK_CHANNEL_ID = '2246162'
        THINGSPK_API_READ_KEY = 'W5552EETGI8TGQJW'
        URL = f'https://api.thingspeak.com/channels/{THINGSPK_CHANNEL_ID}/feeds.json?api_key={THINGSPK_API_READ_KEY}'
        response = requests.get(URL)
        data = response.json()

        df_sensors = pd.DataFrame(data['feeds'])
        df_sensors = df_sensors.astype({'field1':'float'})
        df_sensors = df_sensors.astype({'field2':'float'})


        return df_sensors

    data = generate_data()

    with col1 :
        st.subheader('Temperature over Time')
        fig1 = px.line(data, x="created_at", y="field1", title='Temperature', markers=True)  # Assuming field1 is temperature
        st.plotly_chart(fig1, use_container_width=True)

    
    with col2 :
        st.subheader('pH Level over Time')
        fig2 = px.line(data, x="created_at", y="field2", title='PH', markers=True)  # Assuming field1 is temperature
        st.plotly_chart(fig2, use_container_width=True)


with tab3:
        # Mock GPT-based API
    def get_gpt_response(message, context):
        # In a real scenario, this function would call the GPT API and get a response.
        # For this example, if the message contains "temperature", we return the latest temperature.
        if "temperature" in message.lower():
            return f"The latest temperature reading is {context['Temperature']}°C."
        elif "ph" in message.lower():
            return f"The latest pH reading is {context['pH']}."
        else:
            return "I'm sorry, I don't understand that."



    avg_temperature = data['field1'].mean()
    min_temperature = data['field1'].min()
    max_temperature = data['field1'].max()

    avg_pH = data['field2'].mean()
    min_pH = data['field2'].min()
    max_pH = data['field2'].max()

    # Define the optimal conditions for raising fish
    optimal_conditions = """
    The optimal conditions for raising fish are a pH level between 6.5 and 7.5, and a temperature between 20°C and 25°C.
    """

    # Create the context message

    system_message = f"""
    I am your AI secretary. Based on the data:
    - Average temperature: {avg_temperature:.2f}°C
    - Average pH level: {avg_pH:.2f}
    - Lowest pH level: {min_pH:.2f}
    - Highest pH level: {max_pH:.2f}
    {optimal_conditions}
    Given this information, how can I assist you?
    """


    # Chatbot interface
    user_message = st.text_input("Ask the AI Secretary:")


    if not user_message:
        user_message = "Given this information, what would be your advice?"


    # User's message
    prompt = user_message

    # Response from the API
    completion = openai.ChatCompletion.create(model="gpt-3.5-turbo",
                                            messages=[
                                                {"role": "system", "content": system_message},
                                                {"role": "user", "content": prompt}
                                            ])

    # Extract the response
    response = completion.choices[0].message.content
    st.write(f"AI Secretary: {response}")
