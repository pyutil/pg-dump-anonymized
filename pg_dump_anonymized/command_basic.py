from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import connection, connections

from .bk_anonymized import Dump


class Command(BaseCommand):
    help = ("Backup (anonymized) database. This works for django initial auth solution (auth_user table) and pg_dump."
            " (Customize: in installed package pg_dump_anonymized see to_management_commands/anonymized_dump.py.)")

    @staticmethod
    def get_dump_class():   # if customizing derrived class: rewrite this method, ie.
        return Dump         #    return other Dump object as this one; see to_management_commands/anonymized_dump.py

    def handle(self, *args, **options):
        dump_class = self.get_dump_class()
        dump_class(connections=connections).dump(connection)
