
from django.urls import path
from succession_engine.api import views

urlpatterns = [
    path('scenarios/', views.ScenarioListView.as_view(), name='scenario-list'),
    path('simulate/', views.SimulateSuccessionView.as_view(), name='simulate'),
    path('golden-scenarios/', views.GoldenScenariosView.as_view(), name='golden-scenarios'),
]
