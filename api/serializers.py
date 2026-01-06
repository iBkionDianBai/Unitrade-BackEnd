# api/serializers.py
from rest_framework import serializers
from .models import User, Product, Message, Review
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = {
            'id': str(self.user.id),
            'username': self.user.username,
            'role': self.user.role,
            'avatar': self.user.avatar if self.user.avatar else "",
            'creditScore': self.user.credit_score,
            'bio': self.user.bio,
            'isBanned': self.user.is_banned,
            'wishlist': list(self.user.wishlist.values_list('id', flat=True)),
            'following': list(self.user.following.values_list('id', flat=True))
        }
        return data


class UserSerializer(serializers.ModelSerializer):
    joinDate = serializers.DateTimeField(source='date_joined', read_only=True)
    creditScore = serializers.IntegerField(source='credit_score')
    isBanned = serializers.BooleanField(source='is_banned')

    class Meta:
        model = User
        fields = ['id', 'username', 'avatar', 'role', 'creditScore', 'bio', 'isBanned', 'joinDate', 'wishlist',
                  'following']


class ProductSerializer(serializers.ModelSerializer):
    # 修复：必须提供 queryset 以支持数据读写
    sellerId = serializers.PrimaryKeyRelatedField(source='seller', queryset=User.objects.all())
    # 修复：允许 buyer 为空，解决未售出商品详情页报错导致的 "Product not found"
    buyerId = serializers.PrimaryKeyRelatedField(source='buyer', queryset=User.objects.all(), required=False,
                                                 allow_null=True)
    viewCount = serializers.IntegerField(source='view_count', read_only=True)
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'sellerId', 'buyerId', 'title', 'price', 'description', 'category', 'image', 'status',
                  'viewCount', 'createdAt', 'tags']


class MessageSerializer(serializers.ModelSerializer):
    senderId = serializers.PrimaryKeyRelatedField(source='sender', queryset=User.objects.all())
    receiverId = serializers.PrimaryKeyRelatedField(source='receiver', queryset=User.objects.all())
    type = serializers.CharField(source='msg_type', default='CHAT')

    class Meta:
        model = Message
        fields = ['id', 'senderId', 'receiverId', 'content', 'timestamp', 'is_read', 'type']


class ReviewSerializer(serializers.ModelSerializer):
    # 修复：添加 queryset 参数解决 ImproperlyConfigured 错误
    sellerId = serializers.PrimaryKeyRelatedField(source='seller', queryset=User.objects.all())
    buyerId = serializers.PrimaryKeyRelatedField(source='buyer', queryset=User.objects.all())
    productId = serializers.PrimaryKeyRelatedField(source='product', queryset=Product.objects.all())

    # 额外修复：返回买家用户名，解决前端评价区显示 User_u1 的问题
    buyerName = serializers.ReadOnlyField(source='buyer.username')
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'sellerId', 'buyerId', 'buyerName', 'productId', 'rating', 'content', 'createdAt']