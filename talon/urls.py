from django.urls import path
from .views import (
        TalonToStartView,
        TalonView,
        TalonToEndView,
        TalonTransferToAnotherQueueView,
        TalonToStartView,
        TalonServeStartView,
        TalonServeEndView,
        TalonRemoveView,
        RegistratorTalonView,
        RegistratorTalonRemoveView
    )

urlpatterns = [
    path('', TalonView.as_view(),),
    path('registrator-talon/', RegistratorTalonView.as_view(),),
    path('end/<str:pk>/', TalonToEndView.as_view(),),
    path('transfer/<str:token>/<int:service_id>/', TalonTransferToAnotherQueueView.as_view(),),
    path('start/<str:pk>/', TalonToStartView.as_view(),),
    path('service-start/<str:pk>/', TalonServeStartView.as_view(),),
    path('service-end/<str:pk>/', TalonServeEndView.as_view(),),
    path('remove/<str:pk>/', TalonRemoveView.as_view(),),
    path('registrator/remove/<int:pk>/', RegistratorTalonRemoveView.as_view(),),
]
