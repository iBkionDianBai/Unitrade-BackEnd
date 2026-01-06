# api/management/commands/seed_bulk.py
from django.core.management.base import BaseCommand
from api.models import User, Product
import random


class Command(BaseCommand):
    help = 'Bulk seed 50+ products and extra users into the database'

    def handle(self, *args, **options):
        self.stdout.write("Starting bulk seed process...")

        # 1. 创建额外的学生用户 (u20 - u34)
        usernames = ['leo_king', 'mia_art', 'noah_dev', 'olivia_lit', 'paul_math',
                     'quinn_bio', 'rose_chem', 'sam_physics', 'tina_sport', 'uma_dance',
                     'victor_eco', 'wendy_law', 'xander_history', 'yara_phil', 'zane_music']

        new_users = []
        for i, name in enumerate(usernames):
            uid = f"u{20 + i}"
            user, created = User.objects.get_or_create(
                id=uid,
                defaults={
                    'username': name,
                    'role': 'STUDENT',
                    'is_staff': False,
                    'credit_score': random.randint(700, 950),
                    'bio': f"Student at UniTrade. Passionate about {name.split('_')[1]}.",
                    'avatar': f"https://api.dicebear.com/7.x/avataaars/svg?seed={name}"
                }
            )
            if created:
                user.set_password('password123')
                user.save()
            new_users.append(user)

        self.stdout.write(f"Verified {len(new_users)} student users.")

        # 2. 定义商品模板数据 (覆盖所有分类)
        # 分类: 'Books', 'Electronics', 'Furniture', 'Clothing', 'Sports', 'Others'
        templates = {
            'Books': [
                ('Modern Economics', 45, ['finance', 'textbook']),
                ('Python for Beginners', 30, ['coding', 'tech']),
                ('World History Atlas', 25, ['history', 'reference']),
                ('Organic Chemistry Lab Manual', 15, ['science', 'lab']),
                ('Introduction to Psychology', 35, ['social', 'study']),
                ('Calculus Practice Sets', 12, ['math', 'exam']),
                ('English Literature Anthology', 28, ['arts', 'reading']),
                ('Physics Formulas Cheat Sheet', 5, ['science', 'quick']),
                ('Marketing Management 15th Ed', 50, ['business', 'latest']),
                ('Classical Philosophy Reader', 22, ['philosophy', 'books']),
            ],
            'Electronics': [
                ('Wireless Mouse', 15, ['pc', 'logitech']),
                ('Mechanical Keyboard', 85, ['gaming', 'rgb']),
                ('USB-C Hub 7-in-1', 40, ['adapter', 'macbook']),
                ('Noise Cancelling Headphones', 120, ['audio', 'sony']),
                ('Portable Power Bank 20000mAh', 35, ['travel', 'charging']),
                ('Laptop Cooling Pad', 20, ['accessory', 'gaming']),
                ('Bluetooth Speaker', 55, ['music', 'jbl']),
                ('Graphing Calculator TI-84', 70, ['math', 'tools']),
                ('Monitor Stand with Drawer', 30, ['desk', 'work']),
                ('E-Reader Kindle Paperwhite', 95, ['reading', 'tech']),
            ],
            'Furniture': [
                ('Foldable Study Table', 45, ['dorm', 'space-saving']),
                ('LED Desk Lamp', 18, ['lighting', 'study']),
                ('Swivel Desk Chair', 65, ['office', 'comfort']),
                ('Small Bookshelf', 25, ['storage', 'wooden']),
                ('Bedside Organizer', 10, ['hanging', 'storage']),
                ('Bean Bag Chair', 40, ['relax', 'living']),
                ('Full-length Mirror', 35, ['fashion', 'dorm']),
                ('Storage Ottoman', 30, ['furniture', 'dual-use']),
                ('Under-bed Storage Boxes', 15, ['organizer', 'plastic']),
                ('Small Coffee Table', 50, ['living', 'minimalist']),
            ],
            'Clothing': [
                ('Uni Hoodie - Navy', 30, ['campus', 'apparel']),
                ('Formal Suit Jacket', 80, ['interview', 'business']),
                ('Waterproof Raincoat', 45, ['outdoor', 'gear']),
                ('Sneakers - White', 55, ['shoes', 'casual']),
                ('Winter Scarf & Glove Set', 20, ['winter', 'accessories']),
                ('Dorm Slippers', 8, ['indoor', 'soft']),
                ('Graphic T-Shirt', 15, ['casual', 'style']),
                ('Denim Jacket', 40, ['fashion', 'classic']),
                ('Workout Leggings', 25, ['sports', 'yoga']),
                ('Backpack for 15" Laptop', 50, ['bag', 'travel']),
            ],
            'Sports': [
                ('Yoga Mat 6mm', 20, ['fitness', 'pink']),
                ('Adjustable Dumbbells (5kg)', 35, ['gym', 'home']),
                ('Basketball Spalding', 25, ['ball', 'outdoor']),
                ('Tennis Racket Set', 60, ['sport', 'wilson']),
                ('Resistance Bands Set', 15, ['exercise', 'stretch']),
                ('Swimming Goggles', 12, ['pool', 'speedo']),
                ('Jump Rope (Weighted)', 10, ['cardio', 'fitness']),
                ('Cycling Helmet', 30, ['safety', 'bike']),
                ('Soccer Ball', 20, ['team', 'sport']),
                ('Table Tennis Paddles', 25, ['game', 'set']),
            ],
            'Others': [
                ('Electric Kettle', 18, ['kitchen', 'dorm']),
                ('Yoga Foam Roller', 15, ['recovery', 'others']),
                ('Umbrella (Windproof)', 12, ['weather', 'essential']),
                ('Desk Fan (USB)', 10, ['summer', 'small']),
                ('Art Painting Kit', 30, ['hobby', 'drawing']),
                ('Skateboard', 45, ['wheels', 'transport']),
                ('Board Game - Catan', 40, ['fun', 'social']),
                ('Bicycle Lock', 20, ['security', 'bike']),
                ('Reusable Coffee Cup', 15, ['eco', 'kitchen']),
                ('Alarm Clock (Silent)', 12, ['time', 'bedroom']),
            ]
        }

        # 3. 循环生成 60 个商品
        p_count = 0
        for category, items in templates.items():
            for i, (title, price, tags) in enumerate(items):
                pid = f"pbulk_{category[:1].lower()}_{i}"  # 例如 pbulk_b_0
                seller = random.choice(new_users)

                Product.objects.get_or_create(
                    id=pid,
                    defaults={
                        'seller': seller,
                        'title': title,
                        'price': price,
                        'category': category,
                        'status': 'ACTIVE',
                        'tags': tags,
                        'image': f"https://picsum.photos/seed/{pid}/400/300",
                        'description': f"This is a quality {title} available in the campus marketplace. Used but in great condition.",
                        'view_count': random.randint(10, 100)
                    }
                )
                p_count += 1

        self.stdout.write(self.style.SUCCESS(f'Successfully bulk seeded {p_count} products!'))