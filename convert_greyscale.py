from PIL import Image


class ConvertGreyscaleNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "convert_greyscale"
    CATEGORY = "image"
    
    def convert_greyscale(self, image):
        # Use the same approach as in ComfyUI-LogicUtils/io_node.py:
        # image.convert("L") then convert back to RGB.
        import torch
        import numpy as np
        from PIL import Image

        def tensor_to_pil(img_tensor):
            # img_tensor: (H, W, C) in [0,1]
            np_img = (img_tensor.detach().cpu().numpy() * 255.0).clip(0, 255).astype(np.uint8)
            if np_img.shape[-1] == 1:
                np_img = np.repeat(np_img, 3, axis=-1)
            return Image.fromarray(np_img)

        def pil_to_tensor(img_pil):
            np_img = np.array(img_pil).astype(np.float32) / 255.0
            if np_img.ndim == 2:
                np_img = np.stack([np_img] * 3, axis=-1)
            return torch.from_numpy(np_img)

        # Normalize to a list of images (batch)
        batched = False
        if isinstance(image, torch.Tensor) and image.dim() == 4:
            batched = True
            imgs = [image[i] for i in range(image.shape[0])]
        else:
            imgs = [image.squeeze(0) if isinstance(image, torch.Tensor) and image.dim() == 3 else image]

        out_imgs = []
        for img in imgs:
            if not isinstance(img, torch.Tensor):
                raise RuntimeError("Expected IMAGE tensor")
            pil_img = tensor_to_pil(img)
            grey = pil_img.convert("L")
            grey_rgb = grey.convert("RGB")
            out_tensor = pil_to_tensor(grey_rgb)
            # back to (1, H, W, C)
            out_tensor = out_tensor.unsqueeze(0)
            out_imgs.append(out_tensor)

        result = torch.cat(out_imgs, dim=0) if batched else out_imgs[0]
        return (result,)


NODE_CLASS_MAPPINGS = {
    "ConvertGreyscaleNode": ConvertGreyscaleNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ConvertGreyscaleNode": "Convert Greyscale",
}


