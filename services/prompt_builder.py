
from pathlib import Path
from config import BASE_DIR

class PromptBuilder:

    def build_species_illustration(self, species):

        template = (
            BASE_DIR
            / "prompts"
            / "species_illustration.txt"
        ).read_text(
            encoding="utf-8"
        )

        return template.format(
            english=species["english"],
            scientific=species["scientific"],
            habitat=species["habitat"],
            diet=species["diet"],
            external_id=species["external_id"],
        )

    def build_habitat_illustration(self, species):

        return (
            BASE_DIR
            / "prompts"
            / "species_habitat_illustration.txt"
        ).read_text(
            encoding="utf-8"
        )