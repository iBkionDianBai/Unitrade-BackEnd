from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from django.shortcuts import get_object_or_404
from .models import User, Product, Message, Review
from .serializers import UserSerializer, ProductSerializer, MessageSerializer, ReviewSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import MyTokenObtainPairSerializer # 确保导入了它
import decimal  # 处理钱包余额计算

# 自定义权限类：检查用户角色是否为 ADMIN
class IsAdminRole(permissions.BasePermission):
    """
    自定义权限：只允许 role 为 ADMIN 的用户访问
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'ADMIN'

# 添加这个自定义视图类
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action in ['admin_list', 'toggle_ban']:
            return [IsAdminRole()]
        if self.action in ['toggle_follow', 'toggle_wishlist']:
            return [permissions.IsAuthenticated()]  # 仅限登录用户
        return [permissions.AllowAny()]

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

    # 管理员接口：获取所有用户列表（支持分页和筛选）
    @action(detail=False, methods=['get'])
    def admin_list(self, request):
        queryset = User.objects.all()
        
        # 筛选：按用户名搜索
        search = request.query_params.get('search')
        if search:
            queryset = queryset.filter(username__icontains=search)
        
        # 筛选：按封禁状态
        is_banned = request.query_params.get('isBanned')
        if is_banned is not None:
            queryset = queryset.filter(is_banned=is_banned.lower() == 'true')
        
        # 筛选：按角色
        role = request.query_params.get('role')
        if role:
            queryset = queryset.filter(role=role)
        
        # 排序
        ordering = request.query_params.get('ordering', '-date_joined')
        queryset = queryset.order_by(ordering)
        
        # 分页
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('pageSize', 10))
        start = (page - 1) * page_size
        end = start + page_size
        
        total = queryset.count()
        users = queryset[start:end]
        
        return Response({
            'results': UserSerializer(users, many=True).data,
            'total': total,
            'page': page,
            'pageSize': page_size,
            'totalPages': (total + page_size - 1) // page_size
        })

    # 管理员接口：封禁/解封用户
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def toggle_ban(self, request, pk=None):
        user = self.get_object()
        user.is_banned = request.data.get('isBanned', False)
        user.save()
        return Response({'status': 'updated'})

    @action(detail=True, methods=['post'])
    def toggle_follow(self, request, pk=None):
        # 获取发起关注请求的用户（即当前 URL 中的 ID 对应的用户）
        user = self.get_object()

        # 获取要被关注的目标用户 ID
        target_id = request.data.get('targetId')
        target_user = get_object_or_404(User, id=target_id)

        # 防止自己关注自己
        if user.id == target_user.id:
            return Response({'error': 'You cannot follow yourself'}, status=400)

        # 切换关注状态
        if target_user in user.following.all():
            user.following.remove(target_user)
        else:
            user.following.add(target_user)

        # 返回更新后的用户信息（包含新的 following 列表）
        return Response(UserSerializer(user).data)

    @action(detail=True, methods=['post'])
    def withdraw(self, request, pk=None):
        user = self.get_object()
        amount = float(request.data.get('amount', 0))
        card_number = request.data.get('cardNumber')

        if amount <= 0 or amount > user.wallet_balance:
            return Response({'error': '余额不足或金额非法'}, status=400)

        user.wallet_balance -= decimal.Decimal(amount)
        user.save()
        return Response({'status': 'success', 'newBalance': float(user.wallet_balance)})


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_permissions(self):
        if self.action in ['admin_list', 'toggle_status']:
            return [IsAdminRole()]
        return super().get_permissions()

    def perform_create(self, serializer):
        # 自动将当前登录用户设置为卖家
        serializer.save(seller=self.request.user)

    # 管理员接口：获取所有商品列表（支持分页和筛选）
    @action(detail=False, methods=['get'])
    def admin_list(self, request):
        queryset = Product.objects.all()
        
        # 筛选：按标题搜索
        search = request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(description__icontains=search)
            )
        
        # 筛选：按状态
        product_status = request.query_params.get('status')
        if product_status:
            queryset = queryset.filter(status=product_status)
        
        # 筛选：按分类
        category = request.query_params.get('category')
        if category and category != 'All':
            queryset = queryset.filter(category=category)
        
        # 排序
        ordering = request.query_params.get('ordering', '-created_at')
        queryset = queryset.order_by(ordering)
        
        # 分页
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('pageSize', 10))
        start = (page - 1) * page_size
        end = start + page_size
        
        total = queryset.count()
        products = queryset[start:end]
        
        return Response({
            'results': ProductSerializer(products, many=True).data,
            'total': total,
            'page': page,
            'pageSize': page_size,
            'totalPages': (total + page_size - 1) // page_size
        })
    
    # 管理员接口：切换商品状态
    @action(detail=True, methods=['post'])
    def toggle_status(self, request, pk=None):
        product = self.get_object()
        new_status = request.data.get('status')
        reason = request.data.get('reason', '')
        
        if new_status:
            old_status = product.status
            product.status = new_status
            product.save()
            
            # 如果是下架操作（从非BANNED状态变为BANNED），发送系统消息给卖家
            if old_status != 'BANNED' and new_status == 'BANNED':
                # 获取或创建系统管理员账号
                admin_user = User.objects.filter(role='ADMIN').first()
                if not admin_user:
                    # 如果没有管理员账号，使用第一个超级用户
                    admin_user = User.objects.filter(is_staff=True).first()
                
                if admin_user:
                    # 构建消息内容
                    message_content = f"您的商品「{product.title}」已被管理员下架。\n下架原因：{reason if reason else '违反平台规定'}"
                    
                    # 创建系统消息
                    Message.objects.create(
                        sender=admin_user,
                        receiver=product.seller,
                        content=message_content,
                        msg_type='SYSTEM'
                    )
            
            return Response({'status': 'updated'})
        return Response({'error': 'No status provided'}, status=400)

    def get_queryset(self):
        from django.db.models import Case, When, IntegerField
        
        queryset = Product.objects.all()

        # 搜索功能 (对应 api.ts list params.search)
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(description__icontains=search)
            )

        # 隐藏已售出/确认收货/下架商品 (对应 api.ts list params.hideSold)
        hide_sold = self.request.query_params.get('hideSold')
        if hide_sold == 'true':
            queryset = queryset.exclude(status__in=['SOLD', 'RECEIVED', 'BANNED'])

        # 排序功能 (对应 api.ts list params.sort)
        sort = self.request.query_params.get('sort')
        
        # 定义状态优先级：ACTIVE > 其他状态（SOLD/RECEIVED/BANNED 排在最后）
        status_priority = Case(
            When(status='ACTIVE', then=0),
            default=1,
            output_field=IntegerField()
        )
        
        if sort == 'price_asc':
            queryset = queryset.order_by(status_priority, 'price')
        elif sort == 'price_desc':
            queryset = queryset.order_by(status_priority, '-price')
        elif sort == 'views_desc':
            queryset = queryset.order_by(status_priority, '-view_count')
        else:
            queryset = queryset.order_by(status_priority, '-created_at')

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
        # 获取前端传来的地址
        address = request.data.get('address', '未提供地址')
        buyer = get_object_or_404(User, id=buyer_id)

        if product.status != 'ACTIVE':
            return Response({'error': 'Item not available'}, status=400)

        product.status = 'SOLD'
        product.buyer = buyer
        product.save()

        # 修改系统消息内容，包含买家地址
        Message.objects.create(
            sender=User.objects.filter(is_staff=True).first(),
            receiver=product.seller,
            content=f"恭喜！您的商品 '{product.title}' 已被买家购买。\n买家提供的收货地址/约定地点：{address}",
            msg_type='SYSTEM'
        )
        return Response({'status': 'success'})

    @action(detail=True, methods=['post'])
    def confirm_received(self, request, pk=None):
        product = self.get_object()
        # 验证只有买家可以确认
        if product.buyer_id != request.data.get('buyerId'):
            return Response({'error': '无权操作'}, status=403)

        if product.status != 'SOLD':
            return Response({'error': '商品状态不正确'}, status=400)

        # 更新状态为 RECEIVED 并打款给卖家
        product.status = 'RECEIVED'
        product.save()

        seller = product.seller
        seller.wallet_balance += product.price
        seller.save()

        return Response({'status': 'success'})


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