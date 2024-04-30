FROM vpn.wg1.ahe:5000/aarch64/python:latest

ENV DJANGO_SETTINGS_MODULE=ahe_project.settings

ENV PYTHONPATH /opt/ems/ahe_ems

COPY cover.sh /opt/ems/ahe_ems/cover.sh

COPY obj/ahe_log.cpython-310-aarch64-linux-gnu.so /opt/ems/ahe_ems/
COPY obj/ahe_sys.cpython-310-aarch64-linux-gnu.so /opt/ems/ahe_ems/

COPY ahe_translate/ahe_project /opt/ems/ahe_ems/ahe_project
COPY ahe_translate/ahe-translate /opt/ems/ahe_ems/ahe-translate
COPY ahe_translate/manage.py /opt/ems/ahe_ems/manage.py
COPY ahe_translate/pytest.ini /opt/ems/ahe_ems/pytest.ini
COPY ahe_translate/.coveragerc /opt/ems/ahe_ems/.coveragerc

WORKDIR /opt/ems/ahe_ems/ahe-translate
RUN python -m nuitka --module ahe_translate --include-package=ahe_translate --show-modules

RUN cp /opt/ems/ahe_ems/ahe-translate/*.so /opt/ems/ahe_ems/
WORKDIR /opt/ems/ahe_ems/

