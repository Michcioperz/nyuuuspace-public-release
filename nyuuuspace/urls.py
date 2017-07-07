"""nyuuuspace URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin

import nyuuustead.views

urlpatterns = [
    url(r'^adverb/', admin.site.urls),
    url(r'^account/', include('registration.backends.default.urls')),
    url(r'^account/$', nyuuustead.views.settings_page, name="settings_page"),
    url(r'^u/(?P<username>[\w@\+\-]+)', include([
        url(r'^/follow/$', nyuuustead.views.user_follow_action, name="user_follow_action"),
        url(r'^/unfollow/$', nyuuustead.views.user_unfollow_action, name="user_unfollow_action"),
        url(r'^/$', nyuuustead.views.user_page, name="user_page"),
    ])),
    url(r'^u/$', nyuuustead.views.users_search_page, name="users_search_page"),
    url(r'^u/search.(?P<query>[\w@\+\-]+).json$', nyuuustead.views.users_search, name="users_search"),
    url(r'^(?P<ident>\d+)/', include([
        url(r'^redo/$', nyuuustead.views.hug_rehug_action, name="hug_rehug_action"),
        url(r'^redo/please/$', nyuuustead.views.hug_rehug_question, name="hug_rehug_question"),
        url(r'^return/$', nyuuustead.views.hug_hugback_action, name="hug_hugback_action"),
        url(r'^return/please/$', nyuuustead.views.hug_hugback_question, name="hug_hugback_question"),
        url(r'^$', nyuuustead.views.hug_page, name="hug_page"),
    ])),
    url(r'^everything-is-awesome/$', nyuuustead.views.global_feed, name="global_feed"),
    url(r'^$', nyuuustead.views.main_page, name="main_page"),
]