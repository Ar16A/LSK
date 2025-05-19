import time

from httpx import ConnectError
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_gigachat.chat_models import GigaChat

class TooMany(RuntimeError):
    def __str__(self):
        return "Слишком много запросов. Сервер устал. Попробуйте позже."

class NotEthical(ValueError):
    def __str__(self):
        return "Gigachat отказался отвечать по моральным соображениям."


def summary(text: str) -> str:
    """
    Генерирует краткое содержание текста
    """
    chat = GigaChat(
        credentials="MDNiZWNiMmMtZWE5MS00MDY3LTlkYTAtNmQ5MjE0NmI3M2ViOjg5YTMxZjk1LTY1ZjYtNGE2YS1iYzZkLWRkMTlhYzFhMWQ1Mw==",
        verify_ssl_certs=False,
    )
    messages = [
        SystemMessage(content="""Ты профессиональный суммаризатор текстов. 
                       Сгенерируй краткое содержание на русском языке.""")
    ]
    messages.append(HumanMessage(content=text))
    try:
        response = chat.invoke(messages)
        answer = response.content
        # Проверяем все возможные случаи отказа
        if ("этич" in answer.lower() or
                "отказываюсь" in answer.lower() or
                "blacklist" in str(response) or
                "Не люблю менять тему" in answer):
            raise NotEthical
        return answer
    except ConnectError:
        raise ConnectError
    except NotEthical:
        raise NotEthical
    except Exception as e:
        if "TooMany" in str(e) or "429" in str(e):
            raise TooMany