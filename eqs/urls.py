from django.urls import path
from .views import ( 
    EQSListView,
    EQSRetrieveView,
    )


urlpatterns = [
    path('data/', EQSListView.as_view(),),
    path('data/<int:pk>', EQSRetrieveView.as_view(),),
]
