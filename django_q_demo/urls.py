"""django_q_demo URL Configuration

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
import application.views as views

urlpatterns = [
    path('admin/', admin.site.urls),

    # Sum in View, syncronously
    path('sum-sync/', views.SumView().as_view(), name="sum"),

    # Use tasks to evaluate the sum
    path('sum-start/', views.SumAsyncStartView().as_view(), name="sum-async-start"),
    path('sum-check/', views.SumAsyncProgressView().as_view(), name="sum-async-progress"),

    # Use tasks to run a buggy function
    path('bug-sum-start/', views.BuggySumAsyncStartView().as_view(), name="buggy-sum-async-start"),

    # Use tasks to parallelize a function
    path('split-sum-start/', views.SplitSumAsyncStartView().as_view(), name='split-sum-async-start'),
    path('split-sum-check/', views.SplitSumAsyncProgressView().as_view(), name='split-sum-async-start'),
]
