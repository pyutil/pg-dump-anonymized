"""
Backup (anonymized) database.

This works for django initial auth solution (auth_user table) and pg_dump.
Of course, in this case you need to add pg_dump_anonymized into INSTALLED_APPS to find this management command.

For other scenarios you don't need change INSTALLED_APPS. Instead customize the code:
In installed package pg_dump_anonymized see hints in to_management_commands/anonymized_dump.py.)'
"""

from pg_dump_anonymized.command_basic import Command
