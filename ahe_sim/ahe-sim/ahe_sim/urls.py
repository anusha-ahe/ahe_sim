from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (TestScenarioViewSet, TestExecutionLogViewSet, run_tests, TestScenarioListView, test_scenario_view,
                    condition_view, action_view,
                    fetch_device_variables, TestDetailsListView, device_view, all_list_view)

router = DefaultRouter()
router.register(r'test', TestScenarioViewSet)
router.register(r'log', TestExecutionLogViewSet)


urlpatterns = [
    path('', all_list_view),
    path('logs',TestScenarioListView.as_view(),name='logs'),
    path('test_details',TestDetailsListView.as_view(),name='test_details'),
    path('run_tests',run_tests,name='run_tests'),
    path('condition/', condition_view, name='condition'),
    path('action/', action_view, name='action'),
    path('test_scenario/', test_scenario_view, name='test_scenario'),
    path('device/', device_view, name='device'),
    path('fetch_variables/', fetch_device_variables, name='fetch_variables')]