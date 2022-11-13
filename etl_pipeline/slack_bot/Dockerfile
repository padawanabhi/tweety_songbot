FROM --platform=arm64 python:3.9-rc-alpine3.12

WORKDIR /app

COPY . .

RUN pip install --upgrade pip

RUN pip install -r requirements.txt

CMD ["python", "slack_bot.py"]