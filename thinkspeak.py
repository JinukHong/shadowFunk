import requests
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from statsmodels.tsa.arima.model import ARIMA
from pmdarima import auto_arima


def generate_data(id, rename=None):
        THINGSPK_CHANNEL_ID = id
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

data = generate_data('2246150')



st.write(data)  # Display raw data
st.write(data.info())

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

col1,col2 = st.columns([1,1])
# Or visualize using plotly or any other visualization library
#fig1 = px.line(df, x="created_at", y="field1", title='Temperature', markers=True)  # Assuming field1 is temperature
#fig2 = px.line(df, x="created_at", y="field2", title='PH', markers=True)  # Assuming field1 is temperature
#st.plotly_chart(fig1, use_container_width=True)
#st.plotly_chart(fig2, use_container_width=True)

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
with col1 :
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

with col2 :
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




