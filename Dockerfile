FROM python:3.6
ENV PYTHONUNBUFFERED 1

ENV MAGINE_HOME=/magine

RUN mkdir $MAGINE_HOME
WORKDIR $MAGINE_HOME
ADD requirements.txt requirements-production.txt Magine/requirements.txt $MAGINE_HOME/
ADD . $MAGINE_HOME
RUN pip install -r requirements-production.txt
ENV PYTHONPATH /Magine:$PYTHONPATH
CMD ["uwsgi"]
