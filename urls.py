from django.conf.urls.defaults import *
from bablo.bitems.views import *

urlpatterns = patterns('',
    ('^$', 'django.views.generic.simple.redirect_to', {'url': '/bitems/'}),
    (r'^js/(?P<path>.*)$', 'django.views.static.serve', {'document_root': 'js'}),
    (r'^css/(?P<path>.*)$', 'django.views.static.serve', {'document_root': 'css'}),
    (r'^admin/', include('django.contrib.admin.urls')),
    (r'^bitems/', include('bablo.bitems.urls')),
    (r'^logout/$', 'bablo.bitems.views.logout_view'),
    (r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'login.html'}),
)

