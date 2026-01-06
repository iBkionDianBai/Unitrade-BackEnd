# api/models.py
import random
import uuid

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

def generate_user_id():
    """生成唯一的 ID，如 u + 随机字符，或直接使用 UUID 的一部分"""
    return "u" + uuid.uuid4().hex[:8]

def get_random_avatar():
    # 使用 Dicebear 生成基于随机字符串的头像
    seed = "".join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=8))
    return f"https://api.dicebear.com/7.x/avataaars/svg?seed={seed}"

class User(AbstractUser):
    # 使用自定义 ID 以匹配 mock 中的 'u1', 'u2'
    id = models.CharField(primary_key=True, max_length=20, default=generate_user_id, editable=False)
    avatar = models.URLField(default=get_random_avatar)
    role = models.CharField(max_length=10, default='STUDENT')
    credit_score = models.IntegerField(default=600)
    bio = models.TextField(blank=True)
    is_banned = models.BooleanField(default=False)
    join_date = models.DateField(default=timezone.now)
    wishlist = models.ManyToManyField('Product', blank=True, related_name='wishlisted_by')
    following = models.ManyToManyField('self', symmetrical=False, blank=True, related_name='followers')
    wallet_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)  # 新增钱包字段

class Product(models.Model):
    id = models.CharField(primary_key=True, max_length=50)
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='products')
    buyer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='purchases')
    title = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    category = models.CharField(max_length=50)
    image = models.URLField(max_length=500)
    status = models.CharField(max_length=10, default='ACTIVE')
    view_count = models.IntegerField(default=0)
    tags = models.JSONField(default=list) # 存储 ['tech', 'audio'] 等
    created_at = models.DateTimeField(auto_now_add=True)

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_msgs')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_msgs')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    msg_type = models.CharField(max_length=10, default='CHAT') # 'CHAT' 或 'SYSTEM'

class Review(models.Model):
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_as_seller')
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_as_buyer')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    rating = models.IntegerField()
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)