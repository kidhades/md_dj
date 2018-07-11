from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^qq/authorization/$', views.QQauth_url_view.as_view()),
    url(r'^qq/user/$', views.QQauth_token_view.as_view())
]