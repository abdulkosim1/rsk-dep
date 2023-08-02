from django.urls import path
from .views import (
        UserRetrieveView,
        OperatorQueueView,
        CustomTokenObtainPairView,
        RegistratorQueueView,
        EmployeeShiftView,
    )

urlpatterns = [
    path('retrieve/', UserRetrieveView.as_view()),
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('queue/', OperatorQueueView.as_view(),),
    path('registrator/', RegistratorQueueView.as_view(),),
    path('shift/', EmployeeShiftView.as_view(),),
]
