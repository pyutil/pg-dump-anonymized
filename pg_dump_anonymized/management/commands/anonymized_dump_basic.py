from django.core.management.base import BaseCommand
from django.db import connection


from pg_dump_anonymized.anonymized_dump import Dump


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        Dump().dump(connection)
