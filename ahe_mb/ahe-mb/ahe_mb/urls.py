from ahe_mb.views import home_page, \
    map_list_html, map_detail_html, download_modbus_csv, upload_modbus, \
    bitmpap_list_html, bitmap_detail_html, download_bitmap_csv, upload_bitmap, \
    enum_list_html, enum_detail_html, download_enum_csv, upload_enum, \
    device_map_list_html, device_map_detail_html, download_device_map_csv, upload_device_map, \
    site_device_list_html, site_device_detail_html, download_site_device_csv, upload_site_device, \
    BitMapViewSet, EnumViewSet, MapViewSet, SiteDevicesViewSet, DevicesMapViewSet 

from django.urls import path, include

app_name = "ahe_mb"


urlpatterns = [

    path('map/html/', map_list_html),
    path('map/upload/', upload_modbus),
    path('map/<int:id>/html/', map_detail_html),
    path('map/<int:id>/csv/', download_modbus_csv),
    path('map/', MapViewSet.as_view({'get': 'list', 'post': 'create'}), name="map-list"),
    path('map/<str:name>/', MapViewSet.as_view({'get':'retrieve', 'put':'update'}), name="map-detail"),

    path('bitmap/html/', bitmpap_list_html),
    path('bitmap/upload/', upload_bitmap),
    path('bitmap/<int:id>/html/', bitmap_detail_html),
    path('bitmap/<int:id>/csv/', download_bitmap_csv),
    path('bitmap/', BitMapViewSet.as_view({'get': 'list', 'post': 'create'}), name="bitmap-list"),
    path('bitmap/<str:name>/', BitMapViewSet.as_view({'get':'retrieve', 'put':'update'}), name="bitmap-detail"),

    path('enum/html/', enum_list_html),
    path('enum/upload/', upload_enum),
    path('enum/<int:id>/html/', enum_detail_html),
    path('enum/<int:id>/csv/', download_enum_csv),
    path('enum/', EnumViewSet.as_view({'get': 'list', 'post': 'create'}), name="enum-list"),
    path('enum/<str:name>/', EnumViewSet.as_view({'get':'retrieve', 'put':'update'}), name="enum-detail"),

    path('device-map/html/', device_map_list_html),
    path('device-map/upload/', upload_device_map),
    path('device-map/<int:id>/html/', device_map_detail_html),
    path('device-map/<int:id>/csv/', download_device_map_csv),
    path('device-map/', DevicesMapViewSet.as_view({'get': 'list', 'post': 'create'}), name="device-map-list"),
    path('device-map/<str:name>/', DevicesMapViewSet.as_view({'get':'retrieve', 'put':'update'}), name="device-map-detail"),

    path('site-devices/html/', site_device_list_html),
    path('site-devices/upload/', upload_site_device),
    path('site-devices/<int:id>/html/', site_device_detail_html),
    path('site-devices/<int:id>/csv/', download_site_device_csv),
    path('site-devices/', SiteDevicesViewSet.as_view({'get': 'list', 'post': 'create'}), name="site-devices-list"),
    path('site-devices/<int:site>/', SiteDevicesViewSet.as_view({'get':'retrieve', 'put':'update'}), name="site-devices-detail"),

    path('html/', home_page),
]
