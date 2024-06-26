FROM python:latest

ENV DJANGO_SETTINGS_MODULE=ahe_project.settings

RUN pip install django djangorestframework django_redis mergedeep

RUN pip install pymodbus requests django-cors-headers 

RUN pip install django-crispy-forms crispy-bootstrap4

RUN pip install mysqlclient

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

COPY ahe_sim /opt/ems/ahe_sim
WORKDIR /opt/ems/ahe_sim/ahe-sim
ENV PYTHONPATH /opt/ems/ahe_sim
RUN pip install -e .

COPY config/ /opt/ems/config/

WORKDIR /opt/ems/ahe_sim

CMD ["sleep", "infinity"]


