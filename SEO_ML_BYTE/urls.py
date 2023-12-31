"""SEO_ML_BYTE URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from seo_works import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index),
    path('clear_html.html', views.clear_html),
    path('cat_tag_proceeded.html', views.Cat_Tag_To_ProcessedTermRelationship),
    path('count_term.html', views.count_term),
    path('json_gen.html', views.JSON_Proceed)

]
