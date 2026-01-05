# api/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    # 使用自定义 ID 以匹配 mock 中的 'u1', 'u2'
    id = models.CharField(primary_key=True, max_length=50)
    avatar = models.URLField(max_length=500)
    role = models.CharField(max_length=10, default='STUDENT')
    credit_score = models.IntegerField(default=600)
    bio = models.TextField(blank=True)
    is_banned = models.BooleanField(default=False)
    join_date = models.DateField(auto_now_add=True)
    wishlist = models.ManyToManyField('Product', blank=True, related_name='wishlisted_by')
    following = models.ManyToManyField('self', symmetrical=False, blank=True, related_name='followers')

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