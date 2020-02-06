"""
with only super().dump() this will work like anonymized_dump_basic command,
    ie. works only for django initial auth solution (auth_user table) using pg_dump
you need customize the Dump class (rewrite methods) for other scenario
"""

from pg_dump_anonymized.bk_anonymized import Dump as DumpBasic
from pg_dump_anonymized.command_basic import Command as CommandBasic


class Command(CommandBasic):
    help = 'Backup anonymized version of database.'

    @staticmethod
    def get_dump_class():
        return Dump


class Dump(DumpBasic):
    def dump(self, *args, **kwargs):
        return super().dump(*args, **kwargs)

    # redefine methods from the parent class.
    # see the parent class pg_dump_anonymized.bk_anonymized.Dump to have idea what you need to do in the methods here

    """
    def dump_1_create_table_copies(self, cursor):
        # create table copies for tables which need anonymize

    def dump_2_anonymize_tables(self, cursor):
        # generate faked content into table copies

    def dump_3_dump(self):
        # dump exclude original (private) tables

    def dump_4_fixdump(self):
        # change table names in dump back to proper name

    def dump_5_cleanup(self, cursor):
    """
