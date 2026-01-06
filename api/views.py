from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from django.shortcuts import get_object_or_404
from .models import User, Product, Message, Review
from .serializers import UserSerializer, ProductSerializer, MessageSerializer, ReviewSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import MyTokenObtainPairSerializer # 确保导入了它

# 添加这个自定义视图类
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action in ['admin_list', 'toggle_ban']:
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]  # 允许首页或详情页查看卖家资料

    # 对应 api.ts 中的 users.getProfileData
    @action(detail=True, methods=['get'])
    def profile_data(self, request, pk=None):
        user = self.get_object()
        listings = Product.objects.filter(seller=user, status='ACTIVE')
        sold = Product.objects.filter(seller=user, status='SOLD')
        bought = Product.objects.filter(buyer=user)

        return Response({
            'listings': ProductSerializer(listings, many=True).data,
            'sold': ProductSerializer(sold, many=True).data,
            'bought': ProductSerializer(bought, many=True).data,
            'wishlist': ProductSerializer(user.wishlist.all(), many=True).data,
            'followedUsers': UserSerializer(user.following.all(), many=True).data
        })

    # 对应 api.ts 中的 auth.updateWishlist
    @action(detail=True, methods=['post'])
    def toggle_wishlist(self, request, pk=None):
        user = self.get_object()
        product_id = request.data.get('productId')
        product = get_object_or_404(Product, id=product_id)

        if product in user.wishlist.all():
            user.wishlist.remove(product)
        else:
            user.wishlist.add(product)
        return Response(UserSerializer(user).data)

    # 管理员接口：获取所有用户列表
    @action(detail=False, methods=['get'])
    def admin_list(self, request):
        return Response(UserSerializer(User.objects.all(), many=True).data)

    # 管理员接口：封禁/解封用户
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def toggle_ban(self, request, pk=None):
        user = self.get_object()
        user.is_banned = request.data.get('isBanned', False)
        user.save()
        return Response({'status': 'updated'})


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_queryset(self):
        queryset = Product.objects.all()

        # 搜索功能 (对应 api.ts list params.search)
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(description__icontains=search)
            )

        # 隐藏已售出 (对应 api.ts list params.hideSold)
        hide_sold = self.request.query_params.get('hideSold')
        if hide_sold == 'true':
            queryset = queryset.exclude(status='SOLD')

        # 排序功能 (对应 api.ts list params.sort)
        sort = self.request.query_params.get('sort')
        if sort == 'price_asc':
            queryset = queryset.order_by('price')
        elif sort == 'price_desc':
            queryset = queryset.order_by('-price')
        elif sort == 'views_desc':
            queryset = queryset.order_by('-view_count')
        else:
            queryset = queryset.order_by('-created_at')

        return queryset

    # 获取单个商品时增加浏览量
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.view_count += 1
        instance.save()
        return super().retrieve(request, *args, **kwargs)

    # 购买逻辑
    @action(detail=True, methods=['post'])
    def purchase(self, request, pk=None):
        product = self.get_object()
        buyer_id = request.data.get('buyerId')
        buyer = get_object_or_404(User, id=buyer_id)

        if product.status != 'ACTIVE':
            return Response({'error': 'Item not available'}, status=400)

        product.status = 'SOLD'
        product.buyer = buyer
        product.save()

        # 自动发送系统消息通知卖家
        Message.objects.create(
            sender=User.objects.filter(is_staff=True).first(),
            receiver=product.seller,
            content=f"恭喜！您的商品 '{product.title}' 已被买家购买。",
            msg_type='SYSTEM'
        )
        return Response({'status': 'success'})


    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def toggle_status(self, request, pk=None):
        product = self.get_object()
        new_status = request.data.get('status')
        if new_status:
            product.status = new_status
            product.save()
            return Response({'status': 'updated'})
        return Response({'error': 'No status provided'}, status=400)


class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # 仅返回与当前用户相关的聊天记录
        user_id = self.request.query_params.get('userId')
        if user_id:
            return Message.objects.filter(
                Q(sender_id=user_id) | Q(receiver_id=user_id)
            ).order_by('timestamp')
        return Message.objects.none()


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

    def get_queryset(self):
        # 筛选特定卖家的评价
        seller_id = self.request.query_params.get('sellerId')
        if seller_id:
            return Review.objects.filter(seller_id=seller_id)
        return Review.objects.all()