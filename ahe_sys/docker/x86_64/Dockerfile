FROM vpn.wg1.ahe:5000/x86_64/python:latest

ENV DJANGO_SETTINGS_MODULE=ahe_project.settings

ENV PYTHONPATH /opt/ems/ahe_ems

COPY cover.sh /opt/ems/ahe_ems/cover.sh

COPY ahe_sys/manage.py /opt/ems/ahe_ems/manage.py
COPY ahe_sys/pytest.ini /opt/ems/ahe_ems/pytest.ini
COPY ahe_sys/.coveragerc /opt/ems/ahe_ems/.coveragerc
COPY ahe_sys/ahe_project /opt/ems/ahe_ems/ahe_project
COPY ahe_sys/ahe-sys /opt/ems/ahe_ems/ahe-sys

WORKDIR /opt/ems/ahe_ems/ahe-sys
RUN python -m nuitka --module ahe_sys --include-package=ahe_sys --show-modules

RUN cp /opt/ems/ahe_ems/ahe-sys/*.so /opt/ems/ahe_ems/
WORKDIR /opt/ems/ahe_ems
