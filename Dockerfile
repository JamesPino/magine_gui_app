FROM lolab/magine-complete
USER root
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

ENV MAGINE_HOME=/home/magine
ADD . $MAGINE_HOME
WORKDIR $MAGINE_HOME
ENV PYTHONPATH $MAGINE_HOME:$PYTHONPATH
RUN conda uninstall networkx && conda install networkx=2.3
RUN conda install django=2.2  psycopg2
RUN conda install -c conda-forge uwsgi celery=4.4
RUN pip install django-picklefield django-import-export redis
ENTRYPOINT []
#ENTRYPOINT ["python", "manage.py", "runserver", "0.0.0.0:8000"]
USER magine
CMD ["uwsgi"]
#CMD ["uwsgi", "--master", "--socket", ":8011", "--module", "magine_gui_app.wsgi", "--uid", "www-data", "--gid", "www-data", "--enable-threads"]
