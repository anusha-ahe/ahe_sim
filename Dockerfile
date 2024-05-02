FROM vpn.wg1.ahe:5000/ahe-python:3.10.8-bullseye.27

ENV DJANGO_SETTINGS_MODULE=ahe_project.settings

RUN pip uninstall pymodbus -y

RUN pip install pymodbus


RUN pip show pymodbus

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

COPY config.ini /opt/ems/config.ini
COPY config.py /opt/ems/config.py
COPY sim.py /opt/ems/sim.py

COPY ahe_project /opt/ems/ahe_project
WORKDIR /opt/ems/ahe_project/ahe-project
ENV PYTHONPATH /opt/ems/ahe_project

WORKDIR /opt/ems

COPY db.sqlite3 /opt/ems/db.sqlite3

CMD ["sleep", "infinity"]


