class ImageMemory:
    def __init__(self) -> None:
        self.shelf = {}

    async def put(self, id, image):
        self.shelf[id] = image

    async def get(self, id):
        return self.shelf[id]


IMAGE_MEMORY = None


def get_current_memory():
    global IMAGE_MEMORY
    if not IMAGE_MEMORY:
        IMAGE_MEMORY = ImageMemory()
    return IMAGE_MEMORY
