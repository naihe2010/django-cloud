from django.urls import re_path
from . import views
from . import metrics

urlpatterns = [
    re_path('register/?', views.register),
    re_path('unregister/?', views.unregister),
    re_path('information/?', views.information),
    re_path('get_service/?', views.get_service),
    re_path('metrics/web/?', metrics.web),
    re_path('metrics/api/?', metrics.api),
]
