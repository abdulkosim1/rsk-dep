from django.urls import path


from .views import (
    RegistrationView,
    ActivationView,
    LoginView,
    ClientTalosView,
    RestorePasswordView,
    SetRestoredPasswordView,
    RemoveClientTalonsView,
    RefreshTokenView
)

urlpatterns = [
    path('registration/', RegistrationView.as_view(), name='registration'),
    path('activate/', ActivationView.as_view(), name='activate'),
    path('login/', LoginView.as_view(), name='login'),
    path('token/refresh/', RefreshTokenView.as_view(), name='token_refresh'),
    path('talons/', ClientTalosView.as_view(),),
    path('restore-password/',  RestorePasswordView.as_view(), name='restored_password'),
    path('set-restored-password/', SetRestoredPasswordView.as_view(), name='set_restored_password'),
    path('talon-delete/<int:pk>/', RemoveClientTalonsView.as_view(), name='delete-talon')
]