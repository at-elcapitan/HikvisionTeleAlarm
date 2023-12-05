FROM python:3.10-alpine
WORKDIR /dockerimage
RUN apk add --no-cache gcc musl-dev linux-headers
COPY requirements.txt requirements.txt
COPY files/ files/
RUN pip install -r requirements.txt
ENV TZ=Europe/Kyiv
COPY .env .env
COPY hta/ hta/
CMD ["python", "hta"]
