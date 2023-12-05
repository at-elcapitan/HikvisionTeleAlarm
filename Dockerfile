FROM python:3.10-alpine
WORKDIR /dockerimage
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
ENV TZ=Europe/Kyiv
COPY .env .env
COPY hta/ hta/
CMD ["python", "hta"]
