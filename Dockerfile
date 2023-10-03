FROM python:3.10

EXPOSE 5000

WORKDIR /usr/scr/app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

CMD ["flask", "run", "--host", "0.0.0.0"]

# untuk menjalankan docker dan debug realtime di lokal
# docker run -dp 5000:5000 -w /usr/scr/app -v "$(pwd):/usr/scr/app" flask-api-udemy 
