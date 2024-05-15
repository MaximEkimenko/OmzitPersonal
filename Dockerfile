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

#ENV PYTHONDONTWRITEBYTECODE 1
#ENV PYTHONUNBUFFERED 1
#ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update -y && apt-get install -y gcc curl gnupg build-essential
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
RUN curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list
RUN apt-get update -y && apt-get install -y unixodbc unixodbc-dev tdsodbc freetds-common freetds-bin freetds-dev postgresql
RUN apt-get update && ACCEPT_EULA=Y apt-get -y install mssql-tools msodbcsql17
RUN echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.bash_profile
RUN echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.bashrc
RUN apt-get update



CMD gunicorn main:app --workers 6 --worker-class uvicorn.workers.UvicornWorker --bind=0.0.0.0:5001

# docker build -t personal_api:latest .
# docker run -d --rm --name personal_app_c -p 5001:5001 -v D:\xml_data:/personal_app/xml_data -it personal_api:latest
