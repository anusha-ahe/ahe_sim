FROM vpn.wg1.ahe:5000/aarch64/python:latest

ENV DJANGO_SETTINGS_MODULE=ahe_project.settings

ENV PYTHONPATH /opt/ems/ahe_ems

COPY cover.sh /opt/ems/ahe_ems/cover.sh

COPY obj/ahe_log/manage.py /opt/ems/ahe_ems/manage.py
COPY obj/ahe_log/pytest.ini /opt/ems/ahe_ems/pytest.ini

COPY ahe_log/.coveragerc /opt/ems/ahe_ems/.coveragerc
COPY ahe_log/ahe_project /opt/ems/ahe_ems/ahe_project
COPY ahe_log/ahe-log /opt/ems/ahe_ems/ahe-log

WORKDIR /opt/ems/ahe_ems/ahe-log
RUN python -m nuitka --module ahe_log --include-package=ahe_log --show-modules
RUN cp /opt/ems/ahe_ems/ahe-log/*.so /opt/ems/ahe_ems/
WORKDIR /opt/ems/ahe_ems/

