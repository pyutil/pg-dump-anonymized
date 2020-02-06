# user postgres:
#    as postgres user: create database <newdb> with owner = <origdbowner> template=template0 encoding = 'UTF8'
#                           lc_collate = 'en_US.UTF-8' lc_ctype = 'en_US.UTF-8' connection_limit = -1;
#                      create extension postgis;
#    psql -d <newdb> < /home/mirek/dj/opentrafficweb/opentrafficweb/opentrafficweb-anonymized.sql

import logging
import os
import subprocess
import sys

from faker import Faker


DUMPPATH = os.path.join(os.path.split(os.path.abspath(sys.argv[0]))[0], "dump")  # <project_root>/dump
MODIFIER = "_aa_aa_aa_aa_aa_aa_aa_aa_aa_aa"
FORMAT = '%(asctime) %(message)s'  # this is not necessary because it is a default
logging.basicConfig(format=FORMAT)


class Dump:
    def __init__(self, connections=None,
                 dbname=None, username=None, host='localhost', port='5432',
                 dumppath=DUMPPATH):
        """
        :param connections: if entered, dbname,username,host,port are ignored and taken from connections['default']
        :param dbname:
        :param username:
        :param host:
        :param port:
        :param dumppath: location of the dump; default <project_root>/dump/
        """
        self.dumppath = dumppath
        if connections:
            params = connections['default'].get_connection_params()
            self.dbname = params['database']
            self.username = params['user']
            self.host = params['host']
            self.port = params['port']
        else:
            if dbname is not None:
                self.dbname = dbname
            if username:
                self.username = dbname
            else:
                self.username = username
            self.host = host
            self.port = port

        if not os.path.isdir(self.dumppath):
            os.mkdir(self.dumppath)

    def dump(self, connection):
        with connection.cursor() as cursor:
            self.dump_1_create_table_copies(cursor)
            self.dump_2_anonymize_tables(cursor)
            self.dump_3_dump()
            self.dump_4_fixdump()
            self.dump_5_cleanup(cursor)

    def dump_1_create_table_copies(self, cursor):
        # create table copies for tables which need anonymize
        self.dump_5_cleanup(cursor)
        cursor.execute("create table auth_user%s (like auth_user including all)" % MODIFIER)
        cursor.execute("insert into auth_user%s select * from auth_user" % MODIFIER)

    def dump_2_anonymize_tables(self, cursor):
        # generate faked content into table copies
        fake = Faker()

        cursor.execute("SELECT id, is_superuser, username FROM auth_user")
        users = cursor.fetchall()

        retries = 0
        for user_id, is_superuser, username in users:
            fd1 = fake.date()
            fd2 = fake.date()
            # this is very stupid retry in case of duplicities in unique fields (here: email)
            # if count of retries will grow it must be handled in a different way (ie. modify the entry, ..)
            for _i in range(10):
                try:
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
                    break
                except Exception:
                    retries += 1
        self.logres('auth_user', len(users), retries)

    def dump_3_dump(self):
        # dump exclude original (private) tables
        dumpcmd = "pg_dump"
        # pg_dump -Fc fails by restore :( TODO: sure?
        cmd = ("%s --host=%s --port=%s --dbname=%s --username=%s" % (dumpcmd, self.host, self.port,
                                                                     self.dbname, self.username)).split()
        cmd.append("--exclude-table=auth_user")
        with open("%s/%s-anonymized.sql" % (self.dumppath, self.dbname), "w") as outfile:
            res = subprocess.run(cmd, stdout=outfile).returncode
        self.logdumpres(dumpcmd, res)

    def dump_4_fixdump(self):
        # change table names in dump back to proper name
        subprocess.run(("sed -i s/%s//g %s/%s-anonymized.sql" % (MODIFIER, self.dumppath, self.dbname)).split())

    def dump_5_cleanup(self, cursor):
        cursor.execute("drop table if exists auth_user%s" % MODIFIER)

    @staticmethod
    def logres(tbl, cnt, retries):
        logging.info('%s anonymized: %s rows, %s retries' % (tbl, cnt, retries))

    @staticmethod
    def logdumpres(dumpcmd, res):
        if res:
            logging.error('%s has finished with error value: %i' % (dumpcmd, res))
        else:
            logging.info('%s has finished with no errors', dumpcmd)
