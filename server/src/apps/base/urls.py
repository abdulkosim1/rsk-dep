from django.urls import path
from .views import ( 
    ServiceListView,
    TerminalListView,
    TerminalLoginView,
    TerminalGetTalon,
    DocumentRetrieveView,
    DocumentListView,
    ServiceListView,
    ServiceRetrieveView
    )


urlpatterns = [
    path('terminal/', TerminalListView.as_view(),),
    path('terminal/login/', TerminalLoginView.as_view(),),
    path('terminal/queue/', TerminalGetTalon.as_view(),),
    path('documents/', DocumentListView.as_view(),),
    path('documents/<int:pk>/', DocumentRetrieveView.as_view(),),
    path('services/', ServiceListView.as_view(),),
    path('services/<int:pk>/', ServiceRetrieveView.as_view(),),
]
