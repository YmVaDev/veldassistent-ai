
from storage.database import Database
from providers.image_provider import ImageProvider
from services.illustration_pipeline import IllustrationPipeline

class IllustrationService:

    def __init__(self, db):

        self.db = db
        self.pipeline = IllustrationPipeline()

    def generate_if_missing(self, species):

        if species["image_path"]:
            return

        print(f"Generating illustration for {species}")

        english = species["english"]

        filename = (
            english
            .lower()
            .replace(" ", "_")
        )

        image_path = f"generated/species/{filename}.webp"

        prompt = ""

        image_path = self.pipeline.generate(
            species,
            image_path
        )

        self.db.update_species_image(
            species["id"],
            image_path
        )