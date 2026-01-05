from rest_framework import serializers
from .models import User, Product, Message, Review
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

# 自定义 JWT 登录返回，确保包含用户信息
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        # 将用户信息加入返回的 JSON 中，供前端 App.tsx 保存
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
        fields = ['id', 'username', 'avatar', 'role', 'creditScore', 'bio', 'isBanned', 'joinDate', 'wishlist', 'following']

class ProductSerializer(serializers.ModelSerializer):
    sellerId = serializers.ReadOnlyField(source='seller.id')
    buyerId = serializers.ReadOnlyField(source='buyer.id')
    viewCount = serializers.IntegerField(source='view_count', read_only=True)
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'sellerId', 'buyerId', 'title', 'price', 'description', 'category', 'image', 'status', 'viewCount', 'createdAt', 'tags']

class MessageSerializer(serializers.ModelSerializer):
    senderId = serializers.ReadOnlyField(source='sender.id')
    receiverId = serializers.ReadOnlyField(source='receiver.id')
    type = serializers.CharField(source='msg_type')

    class Meta:
        model = Message
        fields = ['id', 'senderId', 'receiverId', 'content', 'timestamp', 'is_read', 'type']

class ReviewSerializer(serializers.ModelSerializer):
    sellerId = serializers.ReadOnlyField(source='seller.id')
    buyerId = serializers.ReadOnlyField(source='buyer.id')
    productId = serializers.ReadOnlyField(source='product.id')
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'sellerId', 'buyerId', 'productId', 'rating', 'content', 'createdAt']