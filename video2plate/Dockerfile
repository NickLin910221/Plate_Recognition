FROM python:3.10

WORKDIR /app

ADD . ./

RUN pip install -r requirements.txt
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6 -y

CMD ["python", "server_video2plate.py"]