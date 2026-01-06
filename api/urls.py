
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
# 修改导入，引入您自定义的 View
from .views import ProductViewSet, UserViewSet, MessageViewSet, ReviewViewSet, MyTokenObtainPairView

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'users', UserViewSet, basename='user')
router.register(r'messages', MessageViewSet, basename='message')
router.register(r'reviews', ReviewViewSet, basename='review')

urlpatterns = [
    # 将 TokenObtainPairView 替换为 MyTokenObtainPairView
    path('auth/login/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('', include(router.urls)),
]