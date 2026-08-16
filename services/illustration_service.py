from services.illustration_pipeline import IllustrationPipeline

class IllustrationService:

    def __init__(self, db):

        self.db = db
        self.pipeline = IllustrationPipeline()

    def generate_if_missing(self, species):

        if (
            species["species_image_path"]
            and species["habitat_image_path"]
        ):
            return

        print(f"Generating illustration for {species}")

        species_path = (
            f"generated/species/{species['id']}.webp"
        )

        habitat_path = (
            f"generated/habitats/{species['id']}.webp"
        )

        result = self.pipeline.generate(
            species,
            species_path,
            habitat_path
        )

        self.db.update_species_image_path(
            species["id"],
            result["species_image"]
        )

        self.db.update_habitat_image_path(
            species["id"],
            result["habitat_image"]
        )