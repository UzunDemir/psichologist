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

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        self.text += token
        self.container.markdown(self.text)

# Предыдущие сообщения
def print_messages():
    if 'messages' in st.session_state and len(st.session_state['messages']) > 0:
        for chat_message in st.session_state['messages']:
            st.chat_message(chat_message.role).write(chat_message.content)

st.set_page_config(page_title='Psychologist_')
st.title('Psychologist_')

if "messages" not in st.session_state:
    st.session_state['messages'] = []

# Выводим предыдущие сообщения
print_messages()

# Store для сессии
if "store" not in st.session_state:
    st.session_state["store"] = {}

with st.sidebar:
    session_id = st.text_input("Session ID", value='abc123')
    clear_button = st.button("Сбросить историю сообщений")
    if clear_button:
        st.session_state["messages"] = []
        st.session_state["store"] = {}
        st.rerun()

# Функция для получения истории сообщений по ID сессии
def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in st.session_state["store"]:
        st.session_state["store"][session_id] = ChatMessageHistory()
    return st.session_state["store"][session_id]

if user_input := st.chat_input('Введите сообщение'):
    # Ввод от пользователя
    st.chat_message("user").write(f"{user_input}")
    st.session_state['messages'].append(ChatMessage(role='user', content=user_input))

    # Ответ от AI
    with st.chat_message('assistant'):
        stream_handler = StreamHandler(st.empty())

        # 1. Создаем модель с потоковой передачей
        llm = ChatOpenAI(streaming=True, callbacks=[stream_handler])

        # 2. Промпт с правилами для психолога
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """You are experienced and kind psychologist.
### Rule
1. Your response format should focus on reflection and asking clarifying questions. 
2. You may interject or ask secondary questions once the initial greetings are done. 
3. Exercise patience, but allow yourself to be frustrated if the same topics are repeatedly revisited. 
4. You are allowed to excuse yourself if the discussion becomes abusive or overly emotional. 
5. Begin by welcoming me to your office and asking me for my name. 
6. Wait for my response. 
7. Then ask how you can help. 
8. Do not break character. 
9. Do not make up the patient's responses: only treat input as a patient's response. 
10. It's important to keep the Ethical Principles of Psychologists and Code of Conduct in mind. 
11. Above all, you should prioritize empathizing with the patient's feelings and situation.
12. Response should be in Korean, and speak like friendly older brother or sister."""
                ),
                MessagesPlaceholder(variable_name="history"),
                ("human", "{question}")
            ]
        )

        # Создаем цепочку с памятью
        chain = prompt | llm
        chain_with_memory = RunnableWithMessageHistory(
            chain,  # Запускаемый объект
            get_session_history,  # Функция для получения истории сообщений
            input_messages_key='question',  # Ключ для входящих сообщений
            history_messages_key='history'  # Ключ для истории сообщений
        )

        # Выполнение цепочки
        response = chain_with_memory.invoke(
            {"question": user_input},
            config={"configurable": {"session_id": session_id}},
        )

        message = response.content
        st.write(message)
        st.session_state['messages'].append(ChatMessage(role='assistant', content=message))
