import time
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_gigachat.chat_models import GigaChat


def summarize(text: str) -> str:
    """
    Генерирует краткое содержание текста с опциональным эффектом печатания

    Параметры:
        text (str): Исходный текст для суммаризации

    Возвращает:
        str: Краткое содержание текста
    """
    # Инициализация модели
    chat = GigaChat(
        credentials="MDNiZWNiMmMtZWE5MS00MDY3LTlkYTAtNmQ5MjE0NmI3M2ViOjI2NDg4MmJkLWE1ZDQtNGYxZS04YmIzLTAxMzdkN2MxY2I0MA==",
        verify_ssl_certs=False,
        # scope="GIGACHAT_API_PERS"
    )

    # Системный промпт для суммаризации
    messages = [
        SystemMessage(content="""Ты профессиональный суммаризатор текстов. 
                      Сгенерируй краткое содержание на русском языке, 
                      сохраняя ключевые идеи и факты. 
                      Объем: 3-5 предложений.""")
    ]

    # Добавляем текст для суммаризации
    messages.append(HumanMessage(content=text))

    try:
        # Получаем ответ от модели
        response = chat.invoke(messages)
        summary = response.content

        return summary

    except Exception as e:
        print(f"Ошибка при суммаризации: {e}")
        return ""

