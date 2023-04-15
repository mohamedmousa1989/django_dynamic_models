from django.contrib import admin
from django.urls import path
from django.conf.urls import include
from api import views

urlpatterns = [
    path('table/', views.CreateDynamicModelView.as_view(), name='create_dynamic_model'),
    path('table/<int:model_id>/', views.UpdateDynamicModelView.as_view(), name='update_dynamic_model'),
    path('table/<int:model_id>/row/', views.PopulateDynamicModelView.as_view(), name='populate_dynamic_model'),
    path('table/<int:model_id>/rows/', views.ListDynamicModelRowsView.as_view(), name='list_dynamic_model_data')
]