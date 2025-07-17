"""
Management command to seed some test data for development.
Usage: python manage.py seed_data
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from users.models import Author, Follow
from api.models import Post, Comment


class Command(BaseCommand):
    help = 'Seeds the database with test data for development'

    def handle(self, *args, **options):
        self.stdout.write('Seeding database...')

        # Create admin user
        if not Author.objects.filter(username='admin').exists():
            admin = Author.objects.create_user(
                username='admin',
                email='admin@innkeeper.local',
                password='admin123',
                display_name='Admin User',
                role='admin',
                is_approved=True,
                is_staff=True,
                is_superuser=True,
                bio='Node administrator'
            )
            self.stdout.write(f'  Created admin user (password: admin123)')
        else:
            admin = Author.objects.get(username='admin')
            self.stdout.write('  Admin user already exists')

        # Create some regular users
        test_users = [
            {
                'username': 'alice',
                'email': 'alice@example.com',
                'display_name': 'Alice Smith',
                'bio': 'Software developer who loves open source',
            },
            {
                'username': 'bob',
                'email': 'bob@example.com',
                'display_name': 'Bob Johnson',
                'bio': 'CS student, interested in distributed systems',
            },
            {
                'username': 'charlie',
                'email': 'charlie@example.com',
                'display_name': 'Charlie Davis',
                'bio': 'Just here to post stuff',
            },
        ]

        created_users = []
        for user_data in test_users:
            if not Author.objects.filter(username=user_data['username']).exists():
                user = Author.objects.create_user(
                    password='testpass123',
                    is_approved=True,
                    **user_data
                )
                created_users.append(user)
                self.stdout.write(f"  Created user: {user_data['username']} (password: testpass123)")
            else:
                user = Author.objects.get(username=user_data['username'])
                created_users.append(user)

        all_users = [admin] + created_users

        # Create some follow relationships
        if len(created_users) >= 2:
            alice = Author.objects.get(username='alice')
            bob = Author.objects.get(username='bob')
            charlie = Author.objects.get(username='charlie')

            follows = [
                (alice, bob),
                (alice, charlie),
                (bob, alice),
                (charlie, alice),
            ]
            for follower, following in follows:
                Follow.objects.get_or_create(
                    follower=follower,
                    following=following,
                    defaults={'is_accepted': True}
                )
            self.stdout.write('  Created follow relationships')

        # Create some posts
        sample_posts = [
            {
                'author': admin,
                'title': 'Welcome to Innkeeper!',
                'content': 'This is the Innkeeper federated social platform. You can follow people on other nodes too!',
                'visibility': 'PUBLIC',
            },
            {
                'author': created_users[0] if created_users else admin,
                'title': 'Working on a new project',
                'content': 'Been spending a lot of time on this federated social network thing. Distributed systems are really interesting.',
                'categories': 'tech, programming',
                'visibility': 'PUBLIC',
            },
            {
                'author': created_users[1] if len(created_users) > 1 else admin,
                'title': '',
                'content': 'Studying for finals. This database stuff is actually making sense now that I can see it in action.',
                'visibility': 'PUBLIC',
            },
        ]

        for post_data in sample_posts:
            post = Post.objects.create(**post_data)

            # Add a comment to the first post
            if Post.objects.count() <= len(sample_posts):
                Comment.objects.create(
                    author=created_users[1] if len(created_users) > 1 else admin,
                    post=post,
                    content='Nice post!'
                )

        self.stdout.write(f'  Created {len(sample_posts)} sample posts')
        self.stdout.write(self.style.SUCCESS('Done! Database seeded.'))
        self.stdout.write('')
        self.stdout.write('Test accounts:')
        self.stdout.write('  admin / admin123 (superuser)')
        if created_users:
            self.stdout.write('  alice / testpass123')
            self.stdout.write('  bob / testpass123')
            self.stdout.write('  charlie / testpass123')
