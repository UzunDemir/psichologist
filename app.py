import streamlit as st

# Простая функция для обработки ввода пользователя
def simple_psychologist_response(user_input):
    # Здесь можно добавить логику для обработки запроса
    return f"Психолог: {user_input} — это интересно! Можешь рассказать об этом больше?"

# Настройка страницы
st.set_page_config(page_title='Psychologist')
st.title('Psychologist')

# Хранилище для сообщений
if "messages" not in st.session_state:
    st.session_state['messages'] = []

# Вывод сообщений
for msg in st.session_state['messages']:
    st.write(msg)

# Обработка пользовательского ввода
if user_input := st.text_input('Введите ваше сообщение'):
    response = simple_psychologist_response(user_input)
    st.session_state['messages'].append(f"Вы: {user_input}")
    st.session_state['messages'].append(response)
    st.experimental_rerun()
