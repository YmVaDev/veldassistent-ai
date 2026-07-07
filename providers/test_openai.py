
from storage.database import Database
from services.prompt_builder import PromptBuilder
from providers.openai_image_provider import OpenAIImageProvider

db = Database()

species = db.get_species(142)

builder = PromptBuilder()

prompt = builder.build_stage1(species)

provider = OpenAIImageProvider()

provider.generate(
    prompt,
    "generated/test.webp",
    reference_images=[
        "references/illustration_style.png"
    ]
)