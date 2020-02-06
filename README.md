# pg-dump-anonymized
Dump your database (originally designed for django + postgres) with anonymized data (auth_user,..).

## Install

This is more a gist than a final solution.
Possible installation:

    pip install faker
    pip install pg_dump_anonymized

If you want just backup/anonymize the basic django auth solution (with auth_user table) using pg_dump
then add into INSTALLED_APPS:

    'pg_dump_anonymized',

and run:

    ./manage.py anonymized_dump_basic

If you need a different scenario you don't need change your INSTALLED_APPS.
Instead find the installed package in the virtualenvironment and copy file to_management_commands/anonymized_dump.py
to management/commands in the main application of your project (or copy this file from github).

Now

    ./manage.py anonymized_dump

should work exactly as the previous command, but this is not what you want.
You need rewrite the anonymized_dump.Dump class - redefine methods from its parent class.
To do that see pg_dump_anonymized.bk_anonymized.Dump class which methods you need redefine.
