from app.parsers.base_parser import BaseLogParser


class ApacheParser(BaseLogParser):

    def parse(self, **kwargs):

        raise NotImplementedError(
            "ApacheParser is not implemented yet."
        )