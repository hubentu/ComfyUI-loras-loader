class ImageBatchToImageList:
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"image": ("IMAGE",), }}

    RETURN_TYPES = ("IMAGE",)
    OUTPUT_IS_LIST = (True,)
    FUNCTION = "doit"
    CATEGORY = "images"

    def doit(self, image):
        images = [image[i:i + 1, ...] for i in range(image.shape[0])]
        return (images,)


NODE_CLASS_MAPPINGS = {
    "ImageBatchToImageList": ImageBatchToImageList,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ImageBatchToImageList": "Image Batch To Image List",
}


