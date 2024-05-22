from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
from .views import IncomeSourceAPIViewSet,TransactionAPIViewSet,BudgetGoalAPIViewSet, TransactionSplitAPIViewSet,ProfileViewSet,UserViewSet , custom_404_view


# Main router
router = DefaultRouter()
router.register(r'income_sources', IncomeSourceAPIViewSet, basename='income_source')
router.register(r'transactions', TransactionAPIViewSet, basename='transaction')
router.register(r'budget', BudgetGoalAPIViewSet)
router.register(r'profile', ProfileViewSet, basename='profile')
router.register(r'users', UserViewSet)

# Nested router for transaction splits
transactions_router = routers.NestedDefaultRouter(router, r'transactions', lookup='transaction')
transactions_router.register(r'splits', TransactionSplitAPIViewSet, basename='transaction-splits')

urlpatterns= [
    path('', include(router.urls)),
    path('', include(transactions_router.urls)),
]

handler404 = custom_404_view