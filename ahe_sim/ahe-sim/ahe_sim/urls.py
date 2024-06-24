from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (TestScenarioViewSet, TestExecutionLogViewSet, run_tests, TestScenarioListView, test_scenario_view,
                    condition_view, action_view,delete_logs,
                    fetch_device_variables, TestDetailsListView, device_view, all_list_view,delete_device, delete_test)

router = DefaultRouter()
router.register(r'test', TestScenarioViewSet)
router.register(r'log', TestExecutionLogViewSet)


urlpatterns = [
    path('', all_list_view,name='home'),
    path('logs', TestScenarioListView.as_view(), name='logs'),
    path('delete_logs/', delete_logs, name='delete_logs'),
    path('test_details', TestDetailsListView.as_view(),name='test_details'),
    path('run_tests', run_tests, name='run_tests'),
    path('condition/', condition_view, name='condition'),
    path('action/', action_view, name='action'),
    path('test_scenario/', test_scenario_view, name='test_scenario'),
    path('delete_test/', delete_test, name='delete_test'),
    path('device/', device_view, name='device'),
    path('delete_device/', delete_device, name='delete_device'),
    path('fetch_variables/', fetch_device_variables, name='fetch_variables')]