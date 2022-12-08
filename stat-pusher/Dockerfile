FROM python:3.10-slim

WORKDIR /usr/src/stats_pusher

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV ENVIRON=dev

CMD python update_pushgateway_stats.py ${ENVIRON}


