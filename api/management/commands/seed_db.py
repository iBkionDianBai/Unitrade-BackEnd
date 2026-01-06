from django.core.management.base import BaseCommand
from api.models import User, Product, Message, Review
from django.utils.dateparse import parse_datetime


class Command(BaseCommand):
    help = 'Populate database with mockDb.ts data'

    def handle(self, *args, **options):
        # 1. 清理旧数据
        Review.objects.all().delete()
        Message.objects.all().delete()
        Product.objects.all().delete()
        User.objects.all().delete()

        # 2. 导入初始用户
        users_data = [
            {'id': 'u1', 'username': 'admin1', 'role': 'ADMIN', 'credit_score': 999, 'bio': 'Super Admin 1'},
            {'id': 'u2', 'username': 'admin2', 'role': 'ADMIN', 'credit_score': 999, 'bio': 'Super Admin 2'},
            {'id': 'u3', 'username': 'admin3', 'role': 'ADMIN', 'credit_score': 999, 'bio': 'Super Admin 3'},
            {'id': 'u4', 'username': 'student_alice', 'role': 'STUDENT', 'credit_score': 750,
             'bio': 'CS Major, love reading.'},
            {'id': 'u5', 'username': 'student_bob', 'role': 'STUDENT', 'credit_score': 680,
             'bio': 'Selling my old guitar.'},
            {'id': 'u6', 'username': 'charlie_design', 'role': 'STUDENT', 'credit_score': 820,
             'bio': 'Graphic Design student.'},
        ]

        for u in users_data:
            User.objects.create_user(
                id=u['id'],
                username=u['username'],
                password='password123',  # 默认密码
                role=u['role'],
                credit_score=u['credit_score'],
                bio=u['bio'],
                avatar=f"https://picsum.photos/seed/{u['username']}/100/100"
            )
        self.stdout.write("Users seeded.")
        for u in users_data:
            # Set is_staff to True if the role is ADMIN
            is_admin = (u['role'] == 'ADMIN')

            User.objects.create_user(
                id=u['id'],
                username=u['username'],
                password='password123',
                role=u['role'],
                is_staff=is_admin,  # 只有设为 True，IsAdminUser 才会放行
                is_superuser=is_admin,  # 允许进入 Django 原生后台
                credit_score=u['credit_score'],
                bio=u['bio'],
                avatar=f"https://picsum.photos/seed/{u['username']}/100/100"
            )
        # 3. 导入初始商品
        products_data = [
            {'id': 'p1', 'sellerId': 'u4', 'title': 'Calculus Early Transcendentals', 'price': 45, 'category': 'Books',
             'status': 'SOLD', 'tags': ['textbook', 'math']},
            {'id': 'p2', 'sellerId': 'u5', 'title': 'Acoustic Guitar Yamaha', 'price': 150, 'category': 'Others',
             'status': 'ACTIVE', 'tags': ['music', 'instrument']},
            # ... 您可以根据 mockDb.ts 继续添加 ...
        ]

        for p in products_data:
            seller = User.objects.get(id=p['sellerId'])
            Product.objects.create(
                id=p['id'],
                seller=seller,
                title=p['title'],
                price=p['price'],
                category=p['category'],
                status=p['status'],
                tags=p['tags'],
                image=f"https://picsum.photos/seed/{p['id']}/400/300",
                description="Imported from mock data."
            )
        self.stdout.write("Products seeded.")

        # 4. 导入消息和评论
        Message.objects.create(
            sender=User.objects.get(id='u5'),
            receiver=User.objects.get(id='u4'),
            content='Is the math book still available?',
            msg_type='CHAT'
        )

        Review.objects.create(
            seller=User.objects.get(id='u4'),
            buyer=User.objects.get(id='u5'),
            product=Product.objects.get(id='p1'),
            rating=5,
            content='Great seller! Item as described.'
        )

        self.stdout.write(self.style.SUCCESS('Successfully seeded database from mockDb.ts!'))