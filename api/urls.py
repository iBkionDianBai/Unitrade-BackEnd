from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import ProductViewSet, UserViewSet, MessageViewSet, ReviewViewSet

# 使用 Router 自动处理标准接口
router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'users', UserViewSet, basename='user')
router.register(r'messages', MessageViewSet, basename='message')
router.register(r'reviews', ReviewViewSet, basename='review')

urlpatterns = [
    # 身份认证接口 (对应前端 login)
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # 包含所有自动生成的路由
    path('', include(router.urls)),
]