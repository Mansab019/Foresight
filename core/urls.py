from django.urls import path
from core import views

urlpatterns = [
    path('',           views.dashboard,       name='dashboard'),
    path('expenses/',  views.expenses,         name='expenses'),
    path('expenses/upload-csv/', views.upload_csv_view, name='upload_csv'),
    path('uploads/',   views.uploads_list_view, name='uploads'),
    path('uploads/<int:batch_id>/', views.batch_detail_view, name='batch_detail'),
    path('uploads/<int:batch_id>/run/', views.run_batch_pipeline_view, name='run_batch_pipeline'),
    path('predictions/',views.predictions_view,name='predictions'),
    path('alerts/',    views.alerts_view,      name='alerts'),
    path('run-pipeline/',views.run_pipeline_view,name='run_pipeline'),
    path('login/',     views.login_view,       name='login'),
    path('logout/',    views.logout_view,      name='logout'),
]