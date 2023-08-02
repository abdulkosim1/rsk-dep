from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (
    ReportAdminViewSet,
    UserAdminViewSet, 
    ServiceAdminViewSet,
    DocumentAdminViewSet,
    QueueAdminViewSet,
    BranchAdminViewSet,
    WindowAdminViewSet,
    LanguageAdminViewSet,
    ActionsAdminViewSet,
    DayOffAdminViewSet,
    RunningStringModelViewSet,
    CreateRunningStringView,
    AdvertisementModelViewSet,
    CreateAdvertisementView,
    WindowCreateAPIView,
)


router = DefaultRouter()
router.register('users', UserAdminViewSet, 'user')
router.register('services', ServiceAdminViewSet, 'service')
router.register('documents', DocumentAdminViewSet, 'documents')
router.register('queues', QueueAdminViewSet, 'queue')
router.register('branches', BranchAdminViewSet, 'branch')
router.register('windows', WindowAdminViewSet, 'window')
router.register('languages', LanguageAdminViewSet, 'language')
router.register('actions', ActionsAdminViewSet, 'action')
router.register('reports', ReportAdminViewSet, 'report')
router.register('dayoffs', DayOffAdminViewSet, 'dayoff')

urlpatterns = [
    path('post_string/', CreateRunningStringView.as_view(),),
    path('change_string/<int:id>/', RunningStringModelViewSet.as_view({'put': 'update','patch': 'partial_update','delete': 'destroy'})),
    path('post_ad/', CreateAdvertisementView.as_view(),),
    path('change_ad/<int:id>/', AdvertisementModelViewSet.as_view({'put': 'update','patch': 'partial_update','delete': 'destroy'})),
    path('create_window/', WindowCreateAPIView.as_view(),),

]
urlpatterns += router.urls