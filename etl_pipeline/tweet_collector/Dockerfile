FROM --platform=arm64 python:3.9-rc-alpine3.12

WORKDIR /app

COPY . .

RUN pip install --upgrade pip

RUN pip install --trusted-host pypi.python.org -r requirements.txt

CMD ["python", "twitter_client.py"]