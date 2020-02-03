# user postgres:
#    create database <newdb> owner <origdbowner>;
#        or maybe: create database <newdb> with owner = <origdbowner> encoding = 'UTF8'
#                           lc_collate = 'cs_CZ.UTF-8' lc_ctype = 'cs_CZ.UTF-8' connection_limit = -1;
#    psql -d <newdb> < /home/mirek/dj/opentrafficweb/opentrafficweb/opentrafficweb-anonymized.sql

import logging
import subprocess

from faker import Faker


MODIFIER = "_aa_aa_aa_aa_aa_aa_aa_aa_aa_aa"
FORMAT = '%(asctime) %(message)s'  # this is not necessary because it is a default
logging.basicConfig(format=FORMAT)


class Dump:
    def __init__(self, dbname=None):
        if dbname is not None:
            self.dbname = dbname

    def dump(self, connection):
        with connection.cursor() as cursor:
            self.dump_1_create_table_copies(cursor)
            self.dump_2_anonymize_tables(cursor)
            self.dump_3_dump()
            self.dump_4_fixdump()
            self.dump_5_cleanup(cursor)

    def dump_1_create_table_copies(self, cursor):
        self.dump_5_cleanup(cursor)
        cursor.execute("create table auth_user%s (like auth_user including all)" % MODIFIER)
        cursor.execute("insert into auth_user%s select * from auth_user" % MODIFIER)

    def dump_2_anonymize_tables(self, cursor):
        fake = Faker()

        cursor.execute("SELECT id, is_superuser, username FROM auth_user")
        users = cursor.fetchall()

        for user_id, is_superuser, username in users:
            fd1 = fake.date()
            fd2 = fake.date()
            cursor.execute("UPDATE auth_user" + MODIFIER +
                           " SET password = '', email=%s, first_name = %s, last_name = %s, "
                           "date_joined = %s, "
                           "last_login = %s, "
                           "is_superuser = false, is_staff = false, username = %s "
                           "WHERE id = %s", [fake.email(), fake.first_name(), fake.last_name(),
                                             '%s %s' % (min(fd1, fd2), fake.time()),
                                             '%s %s' % (max(fd1, fd2), fake.time()),
                                             ('user_%s' % user_id),  # if is_superuser else username,
                                             user_id])

    def dump_3_dump(self, dbname=None, username=None):
        if dbname is None:
            dbname = self.dbname
        if username is None:
            username = dbname
        cmd = ("pg_dump --dbname=%s --username=%s" % (dbname, username)).split()   # -Fc fails by restore
        cmd.append("--exclude-table=auth_user")
        with open("%s-anonymized.sql" % dbname, "w") as outfile:
            res = subprocess.run(cmd, stdout=outfile).returncode
        if res:
            logging.error('pg_dump has finished with error value: %i' % res)
        else:
            logging.info('pg_dump has finished with no errors')

    def dump_4_fixdump(self, dbname=None):
        if dbname is None:
            dbname = self.dbname
        subprocess.run(("sed -i s/%s//g %s-anonymized.sql" % (MODIFIER, dbname)).split())

    def dump_5_cleanup(self, cursor):
        cursor.execute("drop table if exists auth_user%s" % MODIFIER)
