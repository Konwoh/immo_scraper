from abc import ABC, abstractmethod
from backend.integration.immoscout.parser import ImmoScoutParser
from backend.integration.kleinanzeigen.parser import KleinanzeigenParser
from .base_parser import Parser

class ParserFactory(ABC):
    
    @abstractmethod
    def create_parser(self, site: str) -> Parser:
        pass


class EstateParserCreator(ParserFactory):
    def __init__(self):
        self._parsers = {
            "immoScout": ImmoScoutParser(),
            "kleinanzeigen": KleinanzeigenParser(),
        }

    def create_parser(self, site: str) -> Parser:
        if site in self._parsers:
            return self._parsers[site]
        raise ValueError("Site not available")
