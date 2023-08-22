import streamlit as st
import pandas as pd
import numpy as np
import datetime
import collections
import openai
from streamlit_extras.streaming_write import write
from streamlit_extras.row import row
from streamlit_extras.metric_cards import style_metric_cards
from streamlit_extras.mention import mention
from streamlit_extras.stylable_container import stylable_container
from streamlit_player import st_player
from deep_translator import GoogleTranslator
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from fake_useragent import UserAgent
import plotly.express as px
import plotly.graph_objects as go
import requests
import platform
from statsmodels.tsa.arima.model import ARIMA
from pmdarima import auto_arima

shadowfunk_data = None

def chatwrite(texttowrite):
    lines = texttowrite.split('\n')
    for line in lines:
        yield line + "\n"
        time.sleep(0.05)

@st.cache_data(ttl=300, show_spinner="Retrieving from cache...")
def get_driver(link, wait, firstxpath=None, secondxpath=None, thirdxpath=None, firsttablexpath=None, secondtablexpath=None):
    random_user_agent = user_agent.random
    options = Options()
    options.add_argument('--disable-gpu')
    options.add_argument('--headless')
    options.add_argument(f'--user-agent={random_user_agent}') 
    x = ChromeDriverManager(driver_version="116.0.5845.96").install()
    service = Service(x)
    driver = webdriver.Chrome(service=service, options=options)
    driver.get(link)
    driver.implicitly_wait(wait)
    time.sleep(wait)
    output = []
    if firstxpath:
        firsttext = driver.find_element("xpath", firstxpath).text
        output.append(str(firsttext))
    if secondxpath:
        secondtext = driver.find_element("xpath", secondxpath).text
        output.append(str(secondtext))
    if thirdxpath:
        thirdtext = driver.find_element("xpath", thirdxpath).text
        output.append(str(thirdtext))
    if firsttablexpath:
        firsttable = driver.find_element("xpath", firsttablexpath)
        first_html = firsttable.get_attribute('outerHTML')
        output.append(str(first_html))
    if secondtablexpath:
        secondtable = driver.find_element("xpath", secondtablexpath)
        second_html = secondtable.get_attribute('outerHTML')
        output.append(str(second_html))
    driver.quit()
    return output
    

user_agent = UserAgent()

st.set_page_config(page_title="Seinfarm in Your Hand",
                   page_icon="👨‍🌾",
                   layout="wide",
                   )

openai.api_key = st.secrets["secrets"]['OPENAI_API_KEY']
thingerauth = st.secrets["secrets"]['THINGER_AUTH']

st.title('Sein Farm in your hand')
tab1, tab2, tab3= st.tabs(['Beranda' , 'Statistik', 'Tanya Seina'])

with tab1:

    st.subheader('About Sein Farm')
    col1, col2 = st.columns([1,1])
    towriteincol1 = "**Sein Farm** atau **Sekelama Integrated Farming** adalah salah satu merk inovasi pertanian terpadu di Kota Bandung yang menggabungkan "\
        "unsur – unsur pertanian, peternakan dan perikanan. Sekelama sendiri diambil dari nama jalan dimana Sein Farm berada yaitu di Jalan Sekemala,"\
        " Kelurahan Pasanggrahan, Kecamatan Ujungberung, Kota Bandung. Daerah ini merupakan daerah terluar dari Kota Bandung yang terdapat sawah abadi "\
        "milik Pemkot Bandung. Sein Farm dimaksudkan untuk optimalisasi lahan yaitu menjaga status lahan pertanian, penyediaan pangan, kepedulian hidup "\
        "dan pertanian berkelanjutan."
    col1.markdown(towriteincol1)
    # col2.image("https://buruansae.bandung.go.id/wp-content/uploads/2020/09/WhatsApp-Image-2020-09-19-at-16.34.00-770x428.jpeg")
    col2.image("https://buruansae.bandung.go.id/wp-content/uploads/2021/12/Sein-Farm-2048x819.png")

    mention(
        label="Baca Selengkapnya",
        icon="📖",
        url="https://buruansae.bandung.go.id/index.php/tag/sein-farm/",
    )

    with st.expander("📽️Tonton Video"):
        col1, col2 = st.columns(2)
        with col1:
            st_player("https://www.youtube.com/watch?v=zeITiv8Dt0A", light=True, playing=True)
            st_player("https://www.youtube.com/watch?v=Nl5I5trYKnw", light=True, playing=True)
        with col2:
            st_player("https://www.youtube.com/watch?v=la93X4uoXuw", light=True, playing=True)
            st_player("https://www.youtube.com/watch?v=wHaTpEOUOq8", light=True, playing=True)
            
    google_map_html = """
        https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3960.8752298774416!2d107.71661211431697!3d-6.90552036949942!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x2e68dda940094b3f%3A0x339ec5e7ed736051!2sSEIN%20FARM!5e0!3m2!1sen!2sid!4v1640677700472!5m2!1sen!2sid
        """

    # Embed the Google Map HTML in the Streamlit app
    st.components.v1.iframe(google_map_html, height=300)
    
    # import folium
    # from streamlit_folium import st_folium

    # m = folium.Map(location=[-6.907438,107.715438], zoom_start=16)
    # folium.Marker(
    #     [-6.907438,107.715438], popup="Sein Farm", tooltip="Sein Farm"
    # ).add_to(m)

    # # call to render Folium map in Streamlit, but don't get any data back
    # # from the map (so that it won't rerun the app when the user interacts)
    # st_folium(m, width=400, height=400, returned_objects=[])

with tab2:
    col1,col2 = st.columns(2)
    with col1:
        st.write("Sensors provider:")
    
    with col2:
        # with stylable_container(
        #     key="red_button",
        #     css_styles="""
        #         button {
        #             background-color: red;
        #             color: white;
        #             border-radius: 20px;
        #         }
        #         """,
        # ):
        update_button = st.button("Update Data")
    
        if update_button:
            with st.spinner("Refreshing data..."):
                st.cache_data.clear()
        
    shadowfunk_tab, psyteam_tab, inkofarm_tab, hihello_tab, ie_tab = st.tabs(["shadowfunk", "psyteam", "inko farm", "hihello", "IE"])
    # shadowfunk_tab, psyteam_tab, inkofarm_tab = st.tabs(["shadowfunk", "psyteam", "inko farm"])

    def generate_data(id, rename=None):
        THINGSPK_CHANNEL_ID = id
        THINGSPK_API_READ_KEY = 'W5552EETGI8TGQJW'
        URL = f'https://api.thingspeak.com/channels/{THINGSPK_CHANNEL_ID}/feeds.json?api_key={THINGSPK_API_READ_KEY}'
        response = requests.get(URL)
        data = response.json()

        df_sensors = pd.DataFrame(data['feeds'])
        df_sensors = df_sensors.astype({'field1':'float'})
        df_sensors = df_sensors.astype({'field2':'float'})
        if rename:
          df_sensors.rename(columns={'created_at':'DateTime','field1':'Temperature','field2':'PH'}, inplace=True)
          df_sensors['DateTime'] = pd.to_datetime(df_sensors['DateTime'])
        
        return df_sensors
    
    with shadowfunk_tab:
        st.write('Data provided by ShadowFunk team.')

        col1,col2 = st.columns([1,1])

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
        
        data = generate_data("2246162", "rename")

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
        
        shadowfunk_data = data

#         col1,col2 = st.columns([1,1])

#         # Generate dummy data
        
#         data = generate_data('2246162')

#         with col1 :
#             st.subheader('Temperature over Time')
#             fig1 = px.line(data, x="created_at", y="field1", title='Temperature', markers=True)  # Assuming field1 is temperature
#             fig1.update_xaxes(title_text="Time")
#             fig1.update_yaxes(title_text="°C")
#             st.plotly_chart(fig1, use_container_width=True)

#         with col2 :
#             st.subheader('pH Level over Time')
#             fig2 = px.line(data, x="created_at", y="field2", title='PH', markers=True)  # Assuming field1 is temperature
#             fig2.update_xaxes(title_text="Time")
#             fig2.update_yaxes(title_text="pH")
#             st.plotly_chart(fig2, use_container_width=True)

    with psyteam_tab:
        st.markdown("Taken from Psyteam's [website](https://psyteam-fc61f.web.app/)")

        if platform.system() == "Linux":
            with st.spinner(text="Retrieving data..."):
                retrieved_data = get_driver("https://psyteam-fc61f.web.app/",
                                            7, "/html/body/div/main/div[2]/div[2]/div[1]",
                                            "/html/body/div/main/div[2]/div[2]/div[2]") #temperature and condition
                
                col_t, col_c = st.columns(2)
                col_t.metric(label=retrieved_data[0].split("\n")[0], value=retrieved_data[0].split("\n")[1])
                col_c.metric(label=retrieved_data[1].split("\n")[0], value=retrieved_data[1].split("\n")[1])
                style_metric_cards()

    with inkofarm_tab:
        st.markdown("Data provided by Inko Farm's [dataset](https://thingspeak.com/channels/2246150).")

        col1,col2 = st.columns([1,1])

        # Generate dummy data
        
        data = generate_data('2246150')

        with col1 :
            st.subheader('Temperature over Time')
            fig1 = px.line(data, x="created_at", y="field1", title='Temperature', markers=True)  # Assuming field1 is temperature
            fig1.update_xaxes(title_text="Time")
            fig1.update_yaxes(title_text="°C")
            st.plotly_chart(fig1, use_container_width=True)
            st.components.v1.iframe("https://thingspeak.com/channels/2246150/widgets/698516", height=400)

        with col2 :
            st.subheader('pH Level over Time')
            fig2 = px.line(data, x="created_at", y="field2", title='PH', markers=True)  # Assuming field1 is temperature
            fig2.update_xaxes(title_text="Time")
            fig2.update_yaxes(title_text="pH")
            st.plotly_chart(fig2, use_container_width=True)
            st.components.v1.iframe("https://thingspeak.com/channels/2246150/widgets/698517", height=400)

        
    with hihello_tab:
        st.markdown("Taken from Hihello's [website](https://hifish.serv00.net/)")

        if platform.system() == "Linux":
            with st.spinner(text="Retrieving data..."):
                retrieved_data = get_driver("https://hifish.serv00.net/",
                                            3, "/html/body/div[1]/div[2]/div[2]/div/div[2]/p",
                                            "/html/body/div[1]/div[2]/div[1]/div/div[2]/p", None,
                                            "/html/body/div[2]/div/div[2]/table", "/html/body/div[2]/div/div[1]/table") 
                                            #temperature, ph, phtemptable, feedtable
                
                
                col_t, col_ph = st.columns(2)
                col_t.metric(label=retrieved_data[0].split()[0], value=str(retrieved_data[0].split()[1]))
                col_ph.metric(label=retrieved_data[1].split()[0], value=str(retrieved_data[1].split()[1]))
                style_metric_cards()
                
                phtemp_dfs = pd.read_html(retrieved_data[2])

                if phtemp_dfs:
                    phtemp_df = phtemp_dfs[0]
                    # st.write(df)
                    col1, col2 = st.columns(2)

                    with col1:
                        fig_temp = px.line(phtemp_df, x="Waktu Kejadian", y='Nilai Temp (Celcius) Air', title='pH vs Date and Time')
                        fig_temp.update_xaxes(title_text="Time", autorange='reversed')
                        fig_temp.update_yaxes(title_text="°C")
                        st.plotly_chart(fig_temp, use_container_width=True)
                        
                    with col2:
                        fig_pH = px.line(phtemp_df, x="Waktu Kejadian", y='Nilai pH Air', title='pH vs Date and Time')
                        fig_pH.update_xaxes(title_text="Time", autorange='reversed')
                        fig_pH.update_yaxes(title_text="pH")
                        st.plotly_chart(fig_pH, use_container_width=True)

                else:
                    st.write("No table data found")

                feed_dfs = pd.read_html(retrieved_data[3])
                    
                if feed_dfs:
                    feed_df = feed_dfs[0]
                    # st.write(feed_df)
                    fig = px.scatter(
                        feed_df, 
                        x="Waktu Kejadian",
                        y='Status HiFish',
                        title='Machine Status Scatter Plot'
                    )

                    # Customize the x-axis label and layout
                    fig.update_xaxes(title_text="Time")
                    fig.update_layout(showlegend=False)

                    # Display the plot
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.write("No table data found")
                    
    with ie_tab:
        st.markdown("Taken from ie's Thinger dashboard")

        if platform.system() == "Linux":
            with st.spinner(text="Retrieving data..."):
                retrieved_data = get_driver(f"https://console.thinger.io/dashboards/ESP32?authorization={thingerauth}", 5,
                           "/html/body/ui-view/div/div[1]/div[2]/dashboard/div/div[3]/div/div/div/div/ul/li[2]/div/div[2]/div/div/div/donutchart-widget/div/div/span",
                           "/html/body/ui-view/div/div[1]/div[2]/dashboard/div/div[3]/div/div/div/div/ul/li[3]/div/div[2]/div/div/div/donutchart-widget/div/div/span",
                           "/html/body/ui-view/div/div[1]/div[2]/dashboard/div/div[3]/div/div/div/div/ul/li[4]/div/div[2]/div/div/div/donutchart-widget/div/div/span")
                            # temperature, ammonia, ph

                # pure_temperature = float(str(target_temperature.text).split("\n")[1].strip())
                
                col_t, col_nh3, col_ph = st.columns(3)
                col_t.metric(label="Temperature", value=retrieved_data[0])
                col_nh3.metric(label="Ammonia", value=retrieved_data[1])
                col_ph.metric(label="pH", value=retrieved_data[2])
                style_metric_cards()

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

    # avg_temperature = data['Temperature'].mean()
    # min_temperature = data['Temperature'].min()
    # max_temperature = data['Temperature'].max()

    # avg_pH = data['pH'].mean()
    # min_pH = data['pH'].min()
    # max_pH = data['pH'].max()

    # # Define the optimal conditions for raising fish
    # optimal_conditions = """
    # The optimal conditions for raising fish are a pH level between 6.5 and 7.5, and a temperature between 20°C and 25°C.
    # """

    # # Create the context message

    avg_pH = shadowfunk_data['PH'].mean()
    min_pH = shadowfunk_data['PH'].min()
    max_pH = shadowfunk_data['PH'].max()

    # Define the optimal conditions for raising fish
    optimal_conditions = """
    The optimal conditions for raising fish are a pH level between 6.5 and 7.5, and a temperature between 20°C and 25°C.
    """

    # Create the context message
    # - Average temperature: {avg_temperature:.2f}°C
    system_message = f"""
    Based on the data:
    - Average pH level: {avg_pH:.2f}
    - Lowest pH level: {min_pH:.2f}
    - Highest pH level: {max_pH:.2f}
    {optimal_conditions}
    """

    system_message = ""

    image_row = row([1,8,1], vertical_align="center")
    image_row.empty()
    image_row.image("https://raw.githubusercontent.com/etherealxx/shadowFunx/mj-fixchromedriver/images/seina_banner_cropped_more.png")
    image_row.empty()
    
    # Chatbot interface
    st.caption("Tanya Seina tentang apapun:")
    chat_row = row([9,1])
    user_message = chat_row.text_input("label", placeholder="Ketik disini, kemudian tekan tombol \"Tanya\"", label_visibility="collapsed")
    input_button = chat_row.button("Tanya", use_container_width=True)

    if not user_message:
        # DON'T FORGET TO UNCOMMENT THIS PART AFTER TESTING
        user_message = "Given the data previously, what would be your advice?" 
        pass


    # User's message

    seina_message = "Mulai dari sekarang, kamu akan berperan sebagai Seina, gadis serba tau yang periang, ekspresif, dan ramah. Seina akan menjawab semua pertanyaan seputar Sein Farm "\
    "yang terletak di Pasanggrahan, Kecamatan Ujungberung, Kota Bandung," \
    "dan fakta fakta seputar pertanian dan peternakan ikan. Kamu akan menyapa dengan \"Hai👋, aku Seina, terimakasih sudah bertanya😊\"" \
    ", dan kemudian kamu akan menjawab pertanyaan berikut: "

    ending_message = """
    (Meskipun pertanyaannya berbahasa Inggris, jawablah dengan bahasa Indonesia. Ingat, hindari misinformasi. Bila ragu, minta maaf dan jangan lanjutkan menjawab.).
    """
    prompt = seina_message + user_message + ending_message
    # Response from the API
    if user_message and input_button:
        with st.spinner(text="Tunggu sebentar, Seina masih berpikir🤔..."):
            completion = openai.ChatCompletion.create(model="gpt-3.5-turbo",
                                                    messages=[
                                                        {"role": "system", "content": system_message},
                                                        {"role": "user", "content": prompt}
                                                    ])

        # Extract the response
        response = completion.choices[0].message.content
        with st.spinner(text="Seina sedang menerjemahkan jawaban😉..."):
            translated_response = GoogleTranslator(source='id', target='en').translate(response) 

        # final_response = response + "\n" + "-" * 30 + "\n" + translated_response
        with st.chat_message("assistant", avatar="https://raw.githubusercontent.com/etherealxx/shadowFunx/mj-fixchromedriver/images/seina_icon.png"):
            # st.write(f"{response}")
            write(chatwrite(response))
            st.divider()
            write(chatwrite(translated_response))

hide_footer_style = """
<style>
#MainMenu {visibility: hidden;} 
div.block-container {padding-top:1rem;}
div.block-container {padding-bottom:3rem;}
}
</style>
"""
st.markdown(hide_footer_style, unsafe_allow_html=True)

footer_setup = '''
<script>
// To break out of iframe and access the parent window
const streamlitDoc = window.parent.document;

// Make the replacement
document.addEventListener("DOMContentLoaded", function(event){
    const footer = streamlitDoc.getElementsByTagName("footer")[0];
    footer.innerHTML = `
        Provided by 
        <a href="https://windboy.pusan.ac.kr/issue/issueView?idx=863#solution3282" target="_blank" class="css-z3au9t egzxvld2">shadowfunk</a>
        <img src="https://upload.wikimedia.org/wikipedia/commons/9/9f/Flag_of_Indonesia.svg" alt="Indonesian Flag" height="30">
        <img src="https://upload.wikimedia.org/wikipedia/commons/0/0f/Flag_of_South_Korea.png" alt="Korean Flag" height="30">
        <img src="https://windboy.pusan.ac.kr/assets/files/group/csnsp2.png" alt="Creativity Station Logo" height="30">
    `;
});
</script>
'''

st.components.v1.html(footer_setup)