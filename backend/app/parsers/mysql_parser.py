from app.parsers.base_parser import BaseLogParser


class MySQLParser(BaseLogParser):

    def parse(self, **kwargs):

        raise NotImplementedError(
            "MySQLParser is not implemented yet."
        )