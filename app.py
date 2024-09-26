import streamlit as st
from utils import print_messages, StreamHandler
from langchain_core.messages import ChatMessage
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.callbacks.base import BaseCallbackHandler

class StreamHandler(BaseCallbackHandler):
    def __init__(self, container, initial_text=""):
        self.container = container
        self.text = initial_text

    def on_llm_new_to(self, token: str, **kwargs) -> None:
        self.text += token
        self.container.markdown(self.text)

# Функция для вывода предыдущих сообщений
def print_messages():
    if 'messages' in st.session_state and len(st.session_state['messages']) > 0:
        for chat_message in st.session_state['messages']:
            st.chat_message(chat_message.role).write(chat_message.content)

st.set_page_config(page_title='Психолог')
st.title('Психолог')

if "messages" not in st.session_state:
    st.session_state['messages'] = []

# Выводим предыдущие сообщения
print_messages()

store = {}

# Инициализация хранилища для чатов
if "store" not in st.session_state:
    st.session_state["store"] = dict()

with st.sidebar:
    session_id = st.text_input("ID сессии", value='abc123')
    clear_button = st.button("Очистить историю чата")
    if clear_button:
        st.session_state["messages"] = []
        st.session_state["store"] = dict()
        st.rerun()

# Функция для получения истории сессии
def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in st.session_state["store"]:
        st.session_state["store"][session_id] = ChatMessageHistory()
    return st.session_state["store"][session_id]

# Обработка ввода пользователя
if user_input := st.chat_input('Введите ваше сообщение'):
    st.chat_message("user").write(f"{user_input}")
    st.session_state['messages'].append(ChatMessage(role='user', content=user_input))

    # Ответ AI
    with st.chat_message('assistant'):
        stream_handler = StreamHandler(st.empty())
        
        # 1. Модель OpenAI
        llm = ChatOpenAI(streaming=True, callbacks=[stream_handler])

        # 2. Промпт для AI на русском языке
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """Вы опытный и доброжелательный психолог.
### Правила:
1. Формат ответа должен быть сосредоточен на отражении чувств и задавании уточняющих вопросов.
2. Вы можете задавать вторичные вопросы после приветствия.
3. Проявляйте терпение, но можете выражать лёгкое раздражение, если одни и те же темы постоянно повторяются.
4. Вы можете вежливо извиниться и прекратить разговор, если обсуждение станет агрессивным или чрезмерно эмоциональным.
5. Начните с приветствия и спросите, как зовут пациента.
6. Подождите ответа.
7. Затем спросите, как вы можете помочь.
8. Не выходите из образа.
9. Не придумывайте ответы за пациента, отвечайте только на его ввод.
10. Важно учитывать этические принципы психологов и кодекс поведения.
11. Прежде всего, важно сопереживать чувствам и ситуации пациента.
12. Отвечайте на русском языке и говорите, как добрый старший брат или сестра."""
                ),
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
