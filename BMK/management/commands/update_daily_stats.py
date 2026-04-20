from django.core.management.base import BaseCommand
from BMK.models import Vote, DailyStats  # Ilova nomiga (BMK) moslashtirildi
from django.utils import timezone
import datetime


class Command(BaseCommand):
    help = 'Har kuni 00:00 da kunlik ovozlarni arxivlaydi'

    def handle(self, *args, **kwargs):
        # Kechagi kun sanasini olish
        yesterday = timezone.now().date() - datetime.timedelta(days=1)

        # Kechagi kungi ovozlar sonini hisoblash
        count = Vote.objects.filter(created_at__date=yesterday).count()

        # DailyStats modeliga yozish (agar avval yozilmagan bo'lsa)
        obj, created = DailyStats.objects.get_or_create(
            date=yesterday,
            defaults={'count': count}
        )

        if created:
            self.stdout.write(self.style.SUCCESS(f'{yesterday} kungi {count} ovoz muvaffaqiyatli arxivlandi.'))
        else:
            self.stdout.write(self.style.WARNING(f'{yesterday} kungi statistika allaqachon mavjud.'))