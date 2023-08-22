import streamlit as st
import pandas as pd
import numpy as np
import datetime
import collections
import openai
import requests
import plotly.express as px
import plotly.graph_objects as go
from statsmodels.tsa.arima.model import ARIMA
from pmdarima import auto_arima

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
    
    # def forecast_prophet(df, column_name):
    #     # Prepare data for Prophet
    #     df_prophet = df[['DateTime', column_name]].copy()  # Use .copy() to avoid modifying the original df
    #     df_prophet['DateTime'] = df_prophet['DateTime'].dt.tz_localize(None)  # Remove timezone
    #     df_prophet = df_prophet.rename(columns={'DateTime': 'ds', column_name: 'y'})

    #     # Initialize and fit the model
    #     model = Prophet(yearly_seasonality=True, daily_seasonality=True)
    #     model.fit(df_prophet)

    #     # Create a dataframe for future dates (e.g., 7 days into the future)
    #     future = model.make_future_dataframe(periods=7)

    #     # Forecast values
    #     forecast = model.predict(future)
        
    #     return forecast
    
    def forecast_arima(data, column_name, steps=1):
        # Using auto_arima to find the best parameters
        model_auto = auto_arima(data[column_name], trace=False, error_action='ignore', suppress_warnings=True, stepwise=True)
        #st.write(f"ARIMA order: {model_auto.order}")

        model = ARIMA(data[column_name], order=model_auto.order)

        model_fit = model.fit()
        #st.write(model_fit.summary())
        
        # Forecasting
        last_date = data['DateTime'].iloc[-1]
        forecast_dates = pd.date_range(last_date, periods=steps+1)[1:]
        forecast = model_fit.forecast(steps=steps)

        #st.write(forecast)

        return forecast
    data = generate_data()
    
    #st.write(data)
    # Forecast temperature
    forecast_temperature_arima = forecast_arima(data, 'Temperature', steps=24) # Assuming data is hourly

    # For pH
    forecast_pH_arima = forecast_arima(data, 'PH', steps=24)

    last_real_data_date = data["DateTime"].max()

# This is the last date in your forecasted data. Note: You have to adjust it according to your forecasted DataFrame structure.
    last_forecast_date = last_real_data_date + pd.Timedelta(hours=len(forecast_temperature_arima))
    forecast_start_date = data["DateTime"].max()
    forecast_end_date = forecast_start_date + pd.Timedelta(hours=len(forecast_temperature_arima) - 1) # Subtracting 1 to include the start date
    forecast_dates = pd.date_range(start=forecast_start_date, end=forecast_end_date, freq='H')

# Temperature
    st.markdown('### Temperature and Forecast')
    fig_temp = go.Figure()
    fig_temp.add_trace(go.Scatter(x=data["DateTime"], y=data["Temperature"], mode='lines+markers', name='Actual'))
    fig_temp.add_trace(go.Scatter(x=forecast_dates, y=forecast_temperature_arima, mode='lines', name='Forecast'))
    
    # Here, set the range for the x-axis
    fig_temp.update_layout(xaxis_range=[last_real_data_date - pd.Timedelta(hours=len(data["DateTime"])), last_forecast_date])
    one_day_ago = data["DateTime"].max() - pd.Timedelta(days=1)
    forecast_end_date = data["DateTime"].max() + pd.Timedelta(hours=len(forecast_temperature_arima))

    fig_temp.update_layout(xaxis_range=[one_day_ago, forecast_end_date])

    st.plotly_chart(fig_temp, use_container_width=True)


# PH 
    # st.subheader('pH Level over Time')
    # fig2 = px.line(data, x="created_at", y="field2", title='PH', markers=True)  # Assuming field1 is temperature
    # st.plotly_chart(fig2, use_container_width=True)
    st.markdown('### PH and Forecast')
    fig_ph = go.Figure()
    fig_ph.add_trace(go.Scatter(x=data["DateTime"], y=data["PH"], mode='lines+markers', name='Actual'))
    fig_ph.add_trace(go.Scatter(x=forecast_dates, y=forecast_pH_arima, mode='lines', name='Forecast'))
    # Here, set the range for the x-axis
    fig_ph.update_layout(xaxis_range=[last_real_data_date - pd.Timedelta(hours=len(data["DateTime"])), last_forecast_date])
    one_day_ago = data["DateTime"].max() - pd.Timedelta(days=1)
    forecast_end_date = data["DateTime"].max() + pd.Timedelta(hours=len(forecast_pH_arima))
    fig_ph.update_layout(xaxis_range=[one_day_ago, forecast_end_date])
    st.plotly_chart(fig_ph, use_container_width=True)



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



    avg_temperature = data['Temperature'].mean()
    min_temperature = data['Temperature'].min()
    max_temperature = data['Temperature'].max()

    avg_pH = data['PH'].mean()
    min_pH = data['PH'].min()
    max_pH = data['PH'].max()

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
