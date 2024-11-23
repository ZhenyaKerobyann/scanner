FROM python:latest

WORKDIR /app
COPY . .

RUN pip install -r ./requirements.txt
RUN apt-get update && apt-get install -y supervisor
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
CMD ["supervisord", "-n"]
