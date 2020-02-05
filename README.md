# pg-dump-anonymized
Dump your database (originally designed for django + postgres) with anonymized data (auth_user,..).

## Install

This is more a gist than a final solution.
Possible installation:

    pip install faker
    pip install pg_dump_anonymized

Add into INSTALLED_APPS:

    'pg_dump_anonymized',

Find the installed package in the virtualenvironment and copy file to_project_root/anonymized_dump.py to root of your project (or copy this file from github).
Inside the file set a dbname=..

This should work for the basic django auth_user table and pg_dump. Call:

    ./manage.py anonymized_dump


Under other conditions (other anonymized content, other dump) you should extend the class in <your-project-root>/anonymized_dump.py.
See the parent class which partial methods you could/should rewrite.
