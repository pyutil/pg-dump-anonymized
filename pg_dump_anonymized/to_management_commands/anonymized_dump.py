# with only dbname=.. and super().dump() this works for the basic auth_user


from pg_dump_anonymized.anonymized_dump import Dump as ExampleDump


class Dump(ExampleDump):
    dbname = 'your-db-name'

    def dump(self, *args, **kwargs):
        return super().dump(*args, **kwargs)
