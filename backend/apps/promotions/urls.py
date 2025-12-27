from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PromotionViewSet, PromotionUsageViewSet, ProductSelectorViewSet

router = DefaultRouter()
router.register(r'promotions', PromotionViewSet, basename='promotion')
router.register(r'promotion-usage', PromotionUsageViewSet, basename='promotion-usage')
router.register(r'product-selector', ProductSelectorViewSet, basename='product-selector')

urlpatterns = [
    path('', include(router.urls)),
]
