
from pathlib import Path

class ImageProvider:

	def generate(
	    prompt,
	    output_path,
	    reference_image=None,
	    input_image=None
	)

	    print(f"Generating illustration for {species}")

	    path = Path(output_path)

	    path.parent.mkdir(
	        parents=True,
	        exist_ok=True
	    )

	    path.touch()

	    return str(path)


	    