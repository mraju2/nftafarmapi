FROM python:3.9

WORKDIR /app

ENV FLASK_PORT 5000
ENV LOGLEVEL INFO

EXPOSE 5000

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY logging.conf /
COPY src /app

# CMD /wait && flask run --host=0.0.0.0
CMD python ./app.py
