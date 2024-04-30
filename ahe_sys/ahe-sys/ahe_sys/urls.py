from ahe_sys.views import SiteViewSet, SiteMetaConfViewSet, DeviceTypeViewSet, \
    SiteVariableListViewSet, AheClientViewSet
from rest_framework_nested import routers

from django.urls import path, include

app_name = "ahe_sys"

site_router = routers.SimpleRouter()
site_router.register(r'', SiteViewSet, basename='site')

client_router = routers.SimpleRouter()
client_router.register(r'', AheClientViewSet, basename='client')

device_type_router = routers.SimpleRouter()
device_type_router.register(r'', DeviceTypeViewSet, basename='device')


meta_conf_router = routers.NestedSimpleRouter(site_router, r'', lookup='site')
meta_conf_router.register(r'meta', SiteMetaConfViewSet, basename='meta')

# device_router = routers.NestedSimpleRouter(site_router, r'', lookup='site')
# device_router.register(r'dev', SiteDeviceListViewSet, basename='dev')

site_var_router = routers.NestedSimpleRouter(site_router, r'', lookup='site')
site_var_router.register(r'var', SiteVariableListViewSet, basename='var')


urlpatterns = [
    path('client/', include(client_router.urls), name="client"),
    # path('sites/<pk>', SitesView.as_view(), name="update-site"),
    # path('sites', SitesView.as_view(), name='all-sites'),
    path('device-type/', include(device_type_router.urls), name="device"),
    path('site/', include(site_router.urls), name="site"),
    path('site/', include(meta_conf_router.urls), name="meta"),
    path('site/', include(site_var_router.urls), name="var"),
]
