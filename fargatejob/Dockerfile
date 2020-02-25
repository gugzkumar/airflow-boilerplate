FROM python:3.8.1-slim
WORKDIR /app
COPY ./requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt
ENV PYTHONUNBUFFERED 1
COPY ./ /app
CMD echo hello world
