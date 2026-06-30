
import bird_ai

def analyze(camera, photo):

    if camera == "hibird":
        return bird_ai.analyze(photo)

    return {
        "success": False,
        "error": "Onbekende camera"
    }
