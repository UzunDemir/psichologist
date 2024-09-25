import streamlit as st
from langchain_core.callbacks.base import BaseCallbackHandler
from langchain_core.messages import ChatMessage
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

class StreamHandler(BaseCallbackHandler):
    def __init__(self, container, initial_text=""):
        self.container = container
        self.text = initial_text

    def on_llm_new_to(self, token: str, **kwargs) -> None:
        self.text += token
        self.container.markdown(self.text)

# Функция для вывода сообщений
def print_messages():
    if 'messages' in st.session_state and len(st.session_state['messages']) > 0:
        for chat_message in st.session_state['messages']:
            st.chat_message(chat_message.role).write(chat_message.content)

# Настройка страницы
st.set_page_config(page_title='Psychologist')
st.title('Psychologist')

# Инициализация состояния сессии
if "messages" not in st.session_state:
    st.session_state['messages'] = []

print_messages()  # Вывод предыдущих сообщений

# Хранилище для чатов
if "store" not in st.session_state:
    st.session_state["store"] = dict()

# Боковая панель для управления сессией
with st.sidebar:
    session_id = st.text_input("Session ID", value='abc123')
    clear_button = st.button("Очистить историю сообщений")
    if clear_button:
        st.session_state["messages"] = []
        st.session_state["store"] = dict()
        st.rerun()

# Функция для получения истории сообщений
def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in st.session_state["store"]:
        st.session_state["store"][session_id] = ChatMessageHistory()
    return st.session_state["store"][session_id]

# Обработка пользовательского ввода
if user_input := st.chat_input('Введите ваше сообщение'):
    st.chat_message("user").write(user_input)
    st.session_state['messages'].append(ChatMessage(role='user', content=user_input))

    # Генерация ответа от AI
    with st.chat_message('assistant'):
        stream_handler = StreamHandler(st.empty())

        # Создание модели
        llm = ChatOpenAI(model_name="gpt-3.5-turbo", streaming=True, callbacks=[stream_handler])

        # Создание промпта
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "Вы - опытный и добрый психолог. Ваши ответы должны сосредоточиться на понимании и уточнении вопросов."),
                MessagesPlaceholder(variable_name="history"),
                ("human", "{question}")
            ]
        )

        chain = prompt | llm

        chain_with_memory = (
            RunnableWithMessageHistory(
                chain,
                get_session_history,
                input_messages_key='question',
                history_messages_key='history'
            )
        )

        response = chain_with_memory.invoke(
            {"question": user_input},
            config={"configurable": {"session_id": session_id}},
        )

        message = response.content
        st.write(message)
        st.session_state['messages'].append(ChatMessage(role='assistant', content=message))
