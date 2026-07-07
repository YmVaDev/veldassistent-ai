
from pathlib import Path
from config import BASE_DIR

class PromptBuilder:

    def build_stage1(self, species):

        template = (
            BASE_DIR
            / "prompts"
            / "stage1.txt"
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

    def build_stage2(self, species):

        return (
            BASE_DIR
            / "prompts"
            / "stage2.txt"
        ).read_text(
            encoding="utf-8"
        )