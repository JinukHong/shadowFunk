import streamlit as st
import pandas as pd
import numpy as np
import datetime
import collections
import openai
import requests
import plotly.express as px
from prophet import Prophet
import plotly.graph_objects as go



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
        df_sensors.rename(columns={'created_at':'DateTime','field1':'Temperature','field2':'PH'}, inplace=True)
        df_sensors['DateTime'] = pd.to_datetime(df_sensors['DateTime'])

        return df_sensors
    
    def forecast_data(df, column_name):
        # Prepare data for Prophet
        df_prophet = df[['DateTime', column_name]].copy()  # Use .copy() to avoid modifying the original df
        df_prophet['DateTime'] = df_prophet['DateTime'].dt.tz_localize(None)  # Remove timezone
        df_prophet = df_prophet.rename(columns={'DateTime': 'ds', column_name: 'y'})

        # Initialize and fit the model
        model = Prophet(yearly_seasonality=True, daily_seasonality=True)
        model.fit(df_prophet)

        # Create a dataframe for future dates (e.g., 7 days into the future)
        future = model.make_future_dataframe(periods=7)

        # Forecast values
        forecast = model.predict(future)
        
        return forecast



    data = generate_data()
    st.write(data)
    # Forecast temperature
    forecast_temperature = forecast_data(data, 'Temperature')
    # Forecast pH
    forecast_pH = forecast_data(data, 'PH')


    with col1 :
        # st.subheader('Temperature over Time')
        # fig1 = px.line(data, x="created_at", y="field1", title='Temperature', markers=True)  # Assuming field1 is temperature
        # st.plotly_chart(fig1, use_container_width=True)
        st.markdown('### Temperature and Forecast')
        last_real_data_date = data["DateTime"].max()
        last_forecast_date = forecast_temperature['ds'].max()
        fig_temp = go.Figure()
        fig_temp.add_trace(go.Scatter(x=data["DateTime"], y=data["temperature"], mode='lines+markers', name='Actual'))
        fig_temp.add_trace(go.Scatter(x=forecast_temperature['ds'], y=forecast_temperature['yhat'], mode='lines', name='Forecast'))
        fig_temp.update_layout(xaxis_range=[last_real_data_date - pd.Timedelta(days=1), last_forecast_date + pd.Timedelta(days=1)])
        st.plotly_chart(fig_temp, use_container_width=True)


    
    with col2 :
        # st.subheader('pH Level over Time')
        # fig2 = px.line(data, x="created_at", y="field2", title='PH', markers=True)  # Assuming field1 is temperature
        # st.plotly_chart(fig2, use_container_width=True)
        st.markdown('### pH Level and Forecast')
        last_forecast_date = forecast_temperature['ds'].max()
        fig_temp = go.Figure()
        fig_temp.add_trace(go.Scatter(x=data["DateTime"], y=data["PH"], mode='lines+markers', name='Actual'))
        fig_temp.add_trace(go.Scatter(x=forecast_temperature['ds'], y=forecast_temperature['yhat'], mode='lines', name='Forecast'))
        fig_temp.update_layout(xaxis_range=[last_real_data_date - pd.Timedelta(days=1), last_forecast_date + pd.Timedelta(days=1)])
        st.plotly_chart(fig_temp, use_container_width=True)



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
