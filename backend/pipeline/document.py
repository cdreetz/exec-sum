class Document:
    def __init__(self, sections: dict = None):
        self.sections = sections if sections is not None else {}

    def add_section(self, name: str, content: str):
        self.sections[name] = content

    def get_section(self, name: str) -> str:
        return self.sections.get(name, "")
 