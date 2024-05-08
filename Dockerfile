FROM python:3.12

RUN mkdir /personal_app
WORKDIR /personal_app

COPY req.txt .

RUN pip install -r req.txt

COPY . .

RUN chmod a+x docker/*.sh

RUN apt-get update && apt-get install -y --no-install-recommends \
    unixodbc-dev \
    unixodbc \
    libpq-dev

CMD gunicorn main:app --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind=0.0.0.0:5001


#CMD ["python", "tst_in_personal.py"]
