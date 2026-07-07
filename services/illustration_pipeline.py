
from providers.openai_image_provider import OpenAIImageProvider
from services.prompt_builder import PromptBuilder
from config import REFERENCE_IMAGE

class IllustrationPipeline:

    def __init__(self):

        self.provider = OpenAIImageProvider()
        self.builder = PromptBuilder()

    def generate(
        self,
        species,
        species_image_path,
        habitat_image_path
    ):

        species_image = self.generate_species_illustration(
            species,
            species_image_path
        )

        habitat_image = self.generate_species_habitat_illustration(
            species,
            species_image,
            habitat_image_path
        )

        return {
            "species_image": species_image,
            "habitat_image": habitat_image,
        }


    def generate_species_illustration(
        self,
        species,
        species_image_path
    ):

        prompt = self.builder.build_species_illustration(
            species
        )

        return self.provider.generate(
            prompt=prompt,
            output_path=species_image_path,
            reference_images=[
                REFERENCE_IMAGE
            ]
        )


    def generate_habitat_illustration(
        self,
        species,
        image,
        habitat_image_path
    ):

        prompt = self.builder.build_habitat_illustration(
            species
        )

        return self.provider.generate(
            prompt=prompt,
            output_path=habitat_image_path,
            reference_images=[
                image
            ]
        )