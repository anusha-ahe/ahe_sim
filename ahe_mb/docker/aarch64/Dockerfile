FROM vpn.wg1.ahe:5000/aarch64/python:latest

ENV DJANGO_SETTINGS_MODULE=ahe_project.settings

ENV PYTHONPATH /opt/ems/ahe_ems

COPY cover.sh /opt/ems/ahe_ems/cover.sh

COPY ahe_log.cpython-310-aarch64-linux-gnu.so /opt/ems/ahe_ems/
COPY ahe_sys.cpython-310-aarch64-linux-gnu.so /opt/ems/ahe_ems/

COPY ahe_mb/ahe_project /opt/ems/ahe_ems/ahe_project
COPY ahe_mb/ahe-mb /opt/ems/ahe_ems/ahe-mb
COPY ahe_mb/manage.py /opt/ems/ahe_ems/manage.py
COPY ahe_mb/pytest.ini /opt/ems/ahe_ems/pytest.ini
COPY ahe_mb/.coveragerc /opt/ems/ahe_ems/.coveragerc

WORKDIR /opt/ems/ahe_ems/ahe-mb
RUN python -m nuitka --module ahe_mb --include-package=ahe_mb --show-modules
RUN cp /opt/ems/ahe_ems/ahe-mb/*.so /opt/ems/ahe_ems/
WORKDIR /opt/ems/ahe_ems/

