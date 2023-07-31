from django.urls import path
from .views import BackupView, BackupListView, RestoreView

urlpatterns = [
    path('backup/', BackupView.as_view(), name='backup'),
    path('backups/', BackupListView.as_view(), name='backup-list'),
    path('restore/', RestoreView.as_view(), name='restore'),
]