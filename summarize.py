import time
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_gigachat.chat_models import GigaChat


# Функции для ошибок
def TooMany():
    return "Слишком много запросов. Сервер устал. Попробуйте позже."


def NotEthical():
    return "Gigachat отказался отвечать по моральным соображениям."


def summarize(text: str) -> str:
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
        summary = response.content

        # Проверяем все возможные случаи отказа
        if ("этич" in summary.lower() or
                "отказываюсь" in summary.lower() or
                "blacklist" in str(response) or
                "Не люблю менять тему" in summary):
            return NotEthical()

        return summary

    except Exception as e:
        if "TooMany" in str(e) or "429" in str(e):
            return TooMany()

        print(f"Ошибка при суммаризации: {e}")
        return ""





