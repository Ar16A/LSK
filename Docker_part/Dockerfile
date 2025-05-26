FROM python:3.13.3-slim

WORKDIR /app

RUN apt-get update
RUN python3 -m pip install --upgrade pip

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY remoting.py .
COPY start.py .
RUN python3 start.py

EXPOSE 8000

CMD ["uvicorn", "remoting:app", "--host", "0.0.0.0", "--port", "8000"]