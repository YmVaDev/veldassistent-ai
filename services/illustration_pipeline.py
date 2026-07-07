
from providers.image_provider import ImageProvider
from services.prompt_builder import PromptBuilder

class IllustrationPipeline:

    def __init__(self):

        self.provider = ImageProvider()
        self.builder = PromptBuilder()

    def generate(
        self,
        species,
        output_path
    ):

        image = self.stage1(
            species,
            output_path

        )

        image = self.stage2(
            species,
            image
        )

        return image


    def stage1(
        self,
        species,
        output_path
    ):

        prompt = self.builder.build_stage1(
            species
        )

        return self.provider.generate(
            species,
            prompt,
            output_path
        )


    def stage2(
        self,
        species,
        image
    ):

        return image