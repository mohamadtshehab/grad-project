"""
Management command to test email tasks
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from authentication.tasks import send_password_reset_email, send_welcome_email

User = get_user_model()


class Command(BaseCommand):
    help = 'Test email tasks with Celery'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            help='Email address to send test emails to',
            required=True
        )
        parser.add_argument(
            '--task',
            type=str,
            choices=['reset', 'welcome', 'both'],
            default='both',
            help='Which email task to test'
        )

    def handle(self, *args, **options):
        email = options['email']
        task_type = options['task']

        self.stdout.write(
            self.style.SUCCESS(f'Testing email tasks for: {email}')
        )

        # Test password reset email
        if task_type in ['reset', 'both']:
            self.stdout.write('Queuing password reset email...')
            try:
                task = send_password_reset_email.delay(
                    user_id='test-user-id',
                    reset_code='123456',
                    user_email=email,
                    user_name='Test User'
                )
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Password reset email queued successfully! Task ID: {task.id}'
                    )
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Failed to queue password reset email: {e}')
                )

        # Test welcome email
        if task_type in ['welcome', 'both']:
            self.stdout.write('Queuing welcome email...')
            try:
                task = send_welcome_email.delay(
                    user_id='test-user-id',
                    user_email=email,
                    user_name='Test User'
                )
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Welcome email queued successfully! Task ID: {task.id}'
                    )
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Failed to queue welcome email: {e}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                '\nTo process these tasks, make sure Celery worker is running:'
            )
        )
        self.stdout.write('celery -A graduation_backend worker --loglevel=info')
        self.stdout.write(
            '\nTo monitor tasks:'
        )
        self.stdout.write('celery -A graduation_backend flower')
