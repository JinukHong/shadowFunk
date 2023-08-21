import streamlit as st
import pandas as pd
import numpy as np
import datetime
import collections
import openai
import time
from streamlit_extras.streaming_write import write
from streamlit_extras.row import row
from deep_translator import GoogleTranslator

def chatwrite(texttowrite):
    lines = texttowrite.split('\n')
    for line in lines:
        yield line + "\n"
        time.sleep(0.05)

st.set_page_config(page_title="Seinfarm in Your Hand",
                   page_icon="👨‍🌾",
                   layout="wide",
                   )

openai.api_key = st.secrets["secrets"]['OPENAI_API_KEY']

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
    st.write('Displaying dummy data for temperature and pH levels.')

    col1,col2 = st.columns([1,1])

    # Generate dummy data
    def generate_data():
        time_range = pd.date_range(start="now", periods=60, freq="T")  # Every minute for an hour
        temperature = np.random.uniform(20, 30, 60)  # Random temperature values between 20 and 30
        pH = np.random.uniform(6.5, 7.5, 60)  # Random pH values between 6.5 and 7.5
        return pd.DataFrame({
            "Time": time_range,
            "Temperature": temperature,
            "pH": pH
        })
    data = generate_data()

    with col1 :
        st.subheader('Temperature over Time')
        st.line_chart(data.set_index('Time')['Temperature'])

    
    with col2 :
        st.subheader('pH Level over Time')
        st.line_chart(data.set_index('Time')['pH'])

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

    avg_pH = data['pH'].mean()
    min_pH = data['pH'].min()
    max_pH = data['pH'].max()

    # Define the optimal conditions for raising fish
    optimal_conditions = """
    The optimal conditions for raising fish are a pH level between 6.5 and 7.5, and a temperature between 20°C and 25°C.
    """

    # Create the context message

    system_message = f"""
    Data read from Arduino:
    - Average temperature: {avg_temperature:.2f}°C
    - Average pH level: {avg_pH:.2f}
    - Lowest pH level: {min_pH:.2f}
    - Highest pH level: {max_pH:.2f}
    {optimal_conditions}
    """

    # Chatbot interface
    st.caption("Tanya Seina tentang apapun:")
    # chat_row = row([8,2])
    # user_message = chat_row.text_input("label", placeholder="Ketik disini, kemudian tekan tombol \"Tanya\"", label_visibility="collapsed")
    # input_button = chat_row.button("Tanya", use_container_width=True)
    chat_row1, chat_row2 = st.columns([3,7])
    with chat_row1:
        user_message = st.text_input("label", placeholder="Ketik disini, kemudian tekan tombol \"Tanya\"", label_visibility="collapsed")
    with chat_row2:
       input_button = st.button("✅", use_container_width=True)    

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
.reportview-container .main footer {visibility: hidden !important;}   
#MainMenu {visibility: hidden !important;} 
footer {visibility: hidden !important;} 
div.block-container {padding-top:2rem;}
.css-1jc7ptx, .e1ewe7hr3, .viewerBadge_container__1QSob,
.styles_viewerBadge__1yB5_, .viewerBadge_link__1S137,
.viewerBadge_text__1JaDK {
    display: none;
}
</style>
"""
st.markdown(hide_footer_style, unsafe_allow_html=True)

custom_css = """
<style>
[data-testid=column]:nth-of-type(1) [data-testid=stMarkdown]{
    gap: 0rem;
}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)
