coverage run -m pytest --junitxml=test_report.xml
status=$?
coverage html
coverage xml
coverage report
exit $status
