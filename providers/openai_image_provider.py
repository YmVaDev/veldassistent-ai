
from pathlib import Path
from openai import OpenAI
import base64

class OpenAIImageProvider:

    def __init__(self):

        self.client = OpenAI(
            api_key="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"
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