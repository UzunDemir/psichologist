
import streamlit as st

from transformers import pipeline

# Загрузка модели DialoGPT
chatbot = pipeline("text-generation", model="microsoft/DialoGPT-medium")

st.set_page_config(page_title='Psychologist Chatbot')

# Заголовок приложения
st.title("Виртуальный психолог")

# Поле для ввода сообщения пользователем
user_input = st.text_input("Вы:", "")

if user_input:
    # Генерация ответа
    response = chatbot(user_input, max_length=100, num_return_sequences=1)[0]['generated_text']
    
    # Отображение ответа
    st.text_area("Психолог:", response, height=200)
