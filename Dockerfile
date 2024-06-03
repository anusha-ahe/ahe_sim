FROM python:latest

ENV DJANGO_SETTINGS_MODULE=ahe_project.settings

RUN pip install django djangorestframework django_redis mergedeep

RUN pip install pymodbus requests django-cors-headers 

RUN pip install django-crispy-forms crispy-bootstrap4

COPY ahe_log /opt/ems/ahe_log
WORKDIR /opt/ems/ahe_log/ahe-log
ENV PYTHONPATH /opt/ems/ahe_log
RUN pip install -e .

COPY ahe_sys /opt/ems/ahe_sys
WORKDIR /opt/ems/ahe_sys/ahe-sys
ENV PYTHONPATH /opt/ems/ahe_sys
RUN pip install -e .

COPY ahe_mb /opt/ems/ahe_mb
WORKDIR /opt/ems/ahe_mb/ahe-mb
ENV PYTHONPATH /opt/ems/ahe_mb
RUN pip install -e .

COPY ahe_translate /opt/ems/ahe_translate
WORKDIR /opt/ems/ahe_translate/ahe-translate
ENV PYTHONPATH /opt/ems/ahe_translate
RUN pip install -e .

COPY config/ /opt/ems/config/
COPY slave.py /opt/ems/slave.py
COPY manage.py /opt/ems/manage.py

COPY ahe_project /opt/ems/ahe_project
WORKDIR /opt/ems/ahe_project/ahe-project
ENV PYTHONPATH /opt/ems/ahe_project

WORKDIR /opt/ems

COPY db.sqlite3 /opt/ems/db.sqlite3

CMD ["python3", "manage.py","runserver","0.0.0.0:8100"]


