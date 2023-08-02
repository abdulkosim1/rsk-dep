from django.urls import path

from .views import (
    BranchListView,
    BranchQueueView,
    BranchMainQueueView,
    BranchServiceView,
    GetRunningStringView,
    WindowView,
    AdvertisementView,
    WindowListAPIView,
    MonitorList, 
    MonitorAPIUpdate,
    )

urlpatterns = [
    path('list/', BranchListView.as_view(),),
    path('queue/<int:pk>/',BranchQueueView.as_view(),),
    path('data/branch-queue/<int:branch_id>', BranchMainQueueView.as_view(),),
    path('services/<int:pk>/',BranchServiceView.as_view(),),

    path('get_string/', GetRunningStringView.as_view(),),
    path('window/<int:branch_id>/',WindowView.as_view(),),

    path('get_ad/', AdvertisementView.as_view(),),

    path('window/<int:branch_id>/',WindowView.as_view(),),
    path('get_window/<int:pk>/', WindowListAPIView.as_view(),),

    path('get_monitor/<int:branch_id>/', MonitorList.as_view(),),
    path('update_monitor/<int:pk>/', MonitorAPIUpdate.as_view({'put': 'update','patch': 'partial_update'})),





]
