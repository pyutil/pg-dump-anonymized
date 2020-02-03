import logging
import subprocess

from faker import Faker


MODIFIER = "_aa_aa_aa_aa_aa_aa_aa_aa_aa_aa"
FORMAT = '%(asctime) %(message)s'  # this is not necessary because it is a default
logging.basicConfig(format=FORMAT)


class Dump:
    def dump(self, connection):
        with connection.cursor() as cursor:
            self.dump_1_create_table_copies(cursor)
            self.dump_2_anonymize_tables(cursor)
            self.dump_3_dump("opentrafficweb")
            self.dump_4_fixdump("opentrafficweb")
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

    def dump_3_dump(self, dbname, username=None):
        if username is None:
            username = dbname
        cmd = ("pg_dump -Fc --dbname=%s --username=%s" % (dbname, username)).split()
        cmd.append("--exclude-table=auth_user")
        with open("%s-anonymized.dump" % dbname, "w") as outfile:
            res = subprocess.run(cmd, stdout=outfile).returncode
        if res:
            logging.error('pg_dump has finished with error value: %i' % res)
        else:
            logging.info('pg_dump has finished with no errors')

    def dump_4_fixdump(self, dbname):
        subprocess.run(("sed -i s/%s//g %s-anonymized.dump" % (MODIFIER, dbname)).split())

    def dump_5_cleanup(self, cursor):
        cursor.execute("drop table if exists auth_user%s" % MODIFIER)
