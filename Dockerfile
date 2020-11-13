FROM python:3.7
ENV PYTHONUNBUFFERED 1
RUN mkdir /expo
WORKDIR /expo
ADD requirements.txt /expo/
RUN pip install --upgrade pip && pip install -r requirements.txt
ADD . /expo/
