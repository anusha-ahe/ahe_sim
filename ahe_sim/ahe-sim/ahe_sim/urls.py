from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (TestScenarioViewSet, TestExecutionLogViewSet,run_tests,TestScenarioListView, input_view,
                    fetch_device_variables)

router = DefaultRouter()
router.register(r'test', TestScenarioViewSet)
router.register(r'log', TestExecutionLogViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('tests',TestScenarioListView.as_view(),name='tests'),
    path('run_tests',run_tests,name='run_tests'),
    path('input/', input_view, name='input'),
    path('fetch-variables/', fetch_device_variables, name='fetch_variables')]