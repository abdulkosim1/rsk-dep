from django.urls import path
from .views import (
        SetRatingView,
        BranchTalonStatsView,
    )


urlpatterns = [
    path('rating/', SetRatingView.as_view(),),
    
    path('branch-talon-stats/', BranchTalonStatsView.as_view(), name='branch-talon-stats'),
]
