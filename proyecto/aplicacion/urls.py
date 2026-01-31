from rest_framework.routers import DefaultRouter
from .api import CustomerViewSet, ProductViewSet, OrderViewSet
from rest_framework import routers

router = routers.DefaultRouter()
#router.register('customers', CustomerViewSet)
router.register(r'customers', CustomerViewSet,'customers')
router.register(r'products', ProductViewSet)
router.register(r'orders', OrderViewSet)

urlpatterns = router.urls