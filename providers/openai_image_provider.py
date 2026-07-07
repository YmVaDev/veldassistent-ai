
import base64
from pathlib import Path
from openai import OpenAI

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