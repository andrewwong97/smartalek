from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url(r'^app/', include('app.urls')),
    url(r'^', include('app.urls')),
    url(r'^admin/', admin.site.urls),  # user: andrew, password: andrew!@
]
