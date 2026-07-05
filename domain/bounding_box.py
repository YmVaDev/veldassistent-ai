
class BoundingBox:

    def __init__(self, left, top, right, bottom):

        self.left = left
        self.top = top
        self.right = right
        self.bottom = bottom

    @property
    def width(self):
        return self.right - self.left

    @property
    def height(self):
        return self.bottom - self.top

    def to_dict(self):

        return {
            "left": self.left,
            "top": self.top,
            "right": self.right,
            "bottom": self.bottom
        }

    def __repr__(self):

        return (
            f"BoundingBox("
            f"{self.left}, "
            f"{self.top}, "
            f"{self.right}, "
            f"{self.bottom})"
        )