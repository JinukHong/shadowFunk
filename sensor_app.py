import streamlit as st
import pandas as pd
import numpy as np
import datetime
import collections
import openai
from streamlit_extras.streaming_write import write
from streamlit_extras.row import row
from streamlit_extras.metric_cards import style_metric_cards
from deep_translator import GoogleTranslator
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from fake_useragent import UserAgent
import plotly.express as px
import requests
import platform

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
    towriteincol1 = "Sein Farm atau Sekelama Integrated Farming adalah salah satu merk inovasi pertanian terpadu di Kota Bandung yang menggabungkan "\
        "unsur – unsur pertanian, peternakan dan perikanan. Sekelama sendiri diambil dari nama jalan dimana SEIN FARM berada yaitu di Jalan Sekemala"\
        " kelurahan Pasanggrahan, Kecamatan Ujungberung, Kota Bandung. Daerah ini merupakan daerah terluar dari Kota Bandung yang terdapat sawah abadi "\
        "milik PEMKOT Bandung."
    col1.write(towriteincol1)
    # col2.image("https://buruansae.bandung.go.id/wp-content/uploads/2020/09/WhatsApp-Image-2020-09-19-at-16.34.00-770x428.jpeg")
    col2.image("https://buruansae.bandung.go.id/wp-content/uploads/2021/12/Sein-Farm-2048x819.png")

with tab2:
    st.write("Sensors provider:")
    shadowfunk_tab, psyteam_tab, inkofarm_tab, hihello_tab, ie_tab = st.tabs(["shadowfunk", "psyteam", "inko farm", "hihello", "IE"])
    # shadowfunk_tab, psyteam_tab, inkofarm_tab = st.tabs(["shadowfunk", "psyteam", "inko farm"])

    def generate_data(id):
        THINGSPK_CHANNEL_ID = id
        THINGSPK_API_READ_KEY = 'W5552EETGI8TGQJW'
        URL = f'https://api.thingspeak.com/channels/{THINGSPK_CHANNEL_ID}/feeds.json?api_key={THINGSPK_API_READ_KEY}'
        response = requests.get(URL)
        data = response.json()

        df_sensors = pd.DataFrame(data['feeds'])
        df_sensors = df_sensors.astype({'field1':'float'})
        df_sensors = df_sensors.astype({'field2':'float'})

        return df_sensors
    
    with shadowfunk_tab:
        st.write('Data provided by ShadowFunk team.')

        col1,col2 = st.columns([1,1])

        # Generate dummy data
        
        data = generate_data('2246162')

        with col1 :
            st.subheader('Temperature over Time')
            fig1 = px.line(data, x="created_at", y="field1", title='Temperature', markers=True)  # Assuming field1 is temperature
            fig1.update_xaxes(title_text="Time")
            fig1.update_yaxes(title_text="°C")
            st.plotly_chart(fig1, use_container_width=True)

        with col2 :
            st.subheader('pH Level over Time')
            fig2 = px.line(data, x="created_at", y="field2", title='PH', markers=True)  # Assuming field1 is temperature
            fig2.update_xaxes(title_text="Time")
            fig2.update_yaxes(title_text="pH")
            st.plotly_chart(fig2, use_container_width=True)

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

    # system_message = f"""
    # Data read from Arduino:
    # - Average temperature: {avg_temperature:.2f}°C
    # - Average pH level: {avg_pH:.2f}
    # - Lowest pH level: {min_pH:.2f}
    # - Highest pH level: {max_pH:.2f}
    # {optimal_conditions}
    # """
    system_message = ""

    # Chatbot interface
    st.caption("Tanya Seina tentang apapun:")
    chat_row = row([9,1])
    user_message = chat_row.text_input("label", placeholder="Ketik disini, kemudian tekan tombol \"Tanya\"", label_visibility="collapsed")
    input_button = chat_row.button("Tanya", use_container_width=True)

    if not user_message:
        # DON'T FORGET TO UNCOMMENT THIS PART AFTER TESTING
        # user_message = "Given the data previously, what would be your advice?" 
        pass


    # User's message

    seina_message = "Mulai dari sekarang, kamu akan berperan sebagai Seina, bot serba tau yang periang, ekspresif, dan ramah. Seina akan menjawab semua pertanyaan seputar Sein Farm "\
    "yang terletak di Pasanggrahan, Kecamatan Ujungberung, Kota Bandung," \
    "dan fakta fakta seputar pertanian dan peternakan ikan. Kamu akan menyapa dengan \"Hai👋, aku Seina, terimakasih sudah bertanya😊\"" \
    ", dan kemudian kamu akan menjawab pertanyaan berikut: "

    ending_message = """
    (Ingat, hindari misinformasi. Bila ragu, minta maaf dan jangan lanjutkan menjawab.).
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
        with st.chat_message("assistant", avatar="👧"):
            # st.write(f"{response}")
            write(chatwrite(response))
            st.divider()
            write(chatwrite(translated_response))

hide_footer_style = """
<style>
#MainMenu {visibility: hidden;} 
div.block-container {padding-top:2rem;}
}
</style>
"""
st.markdown(hide_footer_style, unsafe_allow_html=True)

footer_setup = '''
<style>
/* Style for the footer */
.footer-content {
    position: absolute;
    bottom: 0;
    left: 0;
    display: flex;
    justify-content: space-between;
    align-items: center;
    width: 100%;
    padding: 5px;
}

.footer-text {
    margin-right: auto;
}

.footer-logos {
    display: flex;
    align-items: center;
}
</style>

<script>
// To break out of iframe and access the parent window
const streamlitDoc = window.parent.document;

// Make the replacement
document.addEventListener("DOMContentLoaded", function(event){
    const footer = streamlitDoc.getElementsByTagName("footer")[0];
    footer.innerHTML = `
        <div class="footer-content">
            <div class="footer-text">
                Provided by 
                <a href="https://windboy.pusan.ac.kr/issue/issueView?idx=863#solution3282" target="_blank" class="css-z3au9t egzxvld2">shadowfunk</a>
            </div>
            <div class="footer-logos">
                <img src="https://upload.wikimedia.org/wikipedia/commons/9/9f/Flag_of_Indonesia.svg" alt="Indonesian Flag" height="30">
                <img src="https://upload.wikimedia.org/wikipedia/commons/0/0f/Flag_of_South_Korea.png" alt="Korean Flag" height="30">
                <img src="https://windboy.pusan.ac.kr/assets/files/group/csnsp2.png" alt="Creativity Station Logo" height="30">
            </div>
        </div>
    `;
});
</script>
'''

st.components.v1.html(footer_setup)