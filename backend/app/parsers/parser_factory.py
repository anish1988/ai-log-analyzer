"""
Parser Factory

Returns the appropriate parser based on log type.
"""

from app.parsers.apache_parser import ApacheParser
from app.parsers.laravel_parser import LaravelParser
from app.parsers.mysql_parser import MySQLParser


class ParserFactory:

    @staticmethod
    def get_parser(log_type: str):

        print("=" * 100)
        print("PARSER FACTORY")
        print("=" * 100)
        print(f"Requested Log Type : {log_type}")

        #
        # Laravel
        #
        if log_type == "laravel":

            print("Selected Parser : LaravelParser")

            return LaravelParser()

        #
        # Apache
        #
        if log_type.startswith("apache"):

            print("Selected Parser : ApacheParser")

            return ApacheParser()

        #
        # MySQL
        #
        if log_type.startswith("mysql"):

            print("Selected Parser : MySQLParser")

            return MySQLParser()

        raise ValueError(
            f"No parser configured for log type '{log_type}'"
        )