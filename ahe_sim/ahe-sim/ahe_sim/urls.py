from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TestScenarioViewSet, TestExecutionLogViewSet

router = DefaultRouter()
router.register(r'test', TestScenarioViewSet)
router.register(r'log', TestExecutionLogViewSet)


urlpatterns = [
    path('', include(router.urls)),
]