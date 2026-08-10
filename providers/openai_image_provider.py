
import base64
from pathlib import Path
from openai import OpenAI
import os

class OpenAIImageProvider:

    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            raise RuntimeError(
                "OPENAI_API_KEY is not configured"
            )

        self.client = OpenAI(
            api_key=api_key
        )

    def generate(
        self,
        prompt,
        output_path,
        reference_images=None
    ):

        with open(reference_images[0], "rb") as ref:

            result = self.client.images.edit(
                model="gpt-image-1",
                image=ref,
                prompt=prompt
            )

        image = base64.b64decode(
            result.data[0].b64_json
        )


        path = Path(output_path)

        path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with path.open("wb") as f:
            f.write(image)

        return str(path)