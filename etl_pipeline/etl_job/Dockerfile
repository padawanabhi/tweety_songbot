FROM --platform=arm64 python:3.9-rc-alpine3.12

WORKDIR /etl

COPY . .

RUN pip install --upgrade pip

RUN pip install -r requirements.txt

CMD ["python", "etl_job.py"]