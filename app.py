import os
import openai
from elevenlabs import generate, set_api_key
import streamlit as st
from io import BytesIO

# Configurar la clave API de OpenAI desde la variable de entorno
openai.api_key = os.environ["OPENAI_API_KEY"]

# Establecer la clave API de ElevenLabs
set_api_key(os.environ["ELEVENLABS_API_KEY"])

def limit_to_n_words(text, n=100):
    """Limita un texto a un número determinado de palabras."""
    words = text.split()
    return ' '.join(words[:n])

def ask_gpt_and_get_voice_response(user_message):
    with st.spinner('Ángela está pensando...'):
        # Iniciar la conversación con un mensaje del sistema
        messages = [{
            "role": "system",
            "content": "Eres un asistente virtual llamado Ángela, experta en la cultura y arte colombiano. Invitas a las personas a visitar los de arte, museos del oro y la red de bibliotecas del Banco de la República."
        }]
        
        # Agregar el mensaje del usuario a la conversación
        messages.append({"role": "user", "content": user_message})
        
        # Obtener respuesta de GPT-3.5 Turbo
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        
        # Extraer la respuesta en texto y limitarla a 300 palabras
        text_response = limit_to_n_words(response.choices[0].message['content'])
        
        # Agregar la promoción al final
        promo_message = "No olvides visitar los museos del oro y la red de bibliotecas del Banco de la República."
        final_response = f"{text_response} {promo_message}"

        # Convertir la respuesta a audio con ElevenLabs en formato MP3
        audio_data = generate(
            text=final_response,
            voice="ISjMtwHUWrXJSLRtcBf4",
            model="eleven_multilingual_v2",
        )

    return audio_data

# Crear la interfaz de usuario con Streamlit
st.title('Habla con Ángela')
user_message = st.text_input("¿Qué quieres preguntar a Ángela?")

# Verificar si session_state ya tiene los atributos necesarios
if 'last_user_message' not in st.session_state:
    st.session_state.last_user_message = ""
if 'audio_data' not in st.session_state:
    st.session_state.audio_data = None

if user_message and user_message != st.session_state.last_user_message:  
    st.session_state.audio_data = ask_gpt_and_get_voice_response(user_message)
    st.session_state.last_user_message = user_message

if st.session_state.audio_data:
    audio_buffer = BytesIO(st.session_state.audio_data)
    st.audio(audio_buffer, format='audio/mp3', start_time=0)  # Añadir autoplay con start_time=0

    st.download_button(
        label="Descargar respuesta",
        data=audio_buffer,
        file_name="respuesta_angela.mp3",
        mime="audio/mp3"
    )
