
from pathlib import Path

class ImageProvider:

	def generate(
	    self,
	    species,
	    prompt,
	    output_path
	):

	    print(f"Generating illustration for {species}")

	    path = Path(output_path)

	    path.parent.mkdir(
	        parents=True,
	        exist_ok=True
	    )

	    path.touch()

	    return str(path)


	    