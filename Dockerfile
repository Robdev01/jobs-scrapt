FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY reque.txt .
RUN pip install --no-cache-dir -r reque.txt

COPY . .

EXPOSE 9099

CMD ["python", "main.py"]
