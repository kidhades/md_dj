from . import views
from django.conf.urls import url
from rest_framework_jwt.views import obtain_jwt_token

urlpatterns = [
    url(r'^users/$', views.UserView.as_view()),
    url(r'^usernames/(?P<username>\w{5,20})/count/$', views.UsernameCountView.as_view()),
    url(r'^mobiles/(?P<mobiles>\d{11})/count/$', views.MobilesCountView.as_view()),
    url(r'^authorizations/$', obtain_jwt_token),
    url(r'^emails/$', views.EmailView.as_view()),
    url(r'', views.UserDetailView.as_view()),
]