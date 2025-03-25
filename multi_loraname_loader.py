import os
import folder_paths

class MultiLoRAnameLoader:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "index": ("INT", {"default": 0, "min": 0, "max": 99, "step": 1}),
                "LoRAnames": ("STRING", {"multiline": True, "default": "LoRAname1.safetensors\nLoRAname2.safetensors\nLoRAname3.safetensors"}),
            }
        }

    RETURN_TYPES = ("STRING",)  # Simply return a string
    RETURN_NAMES = ("lora_name",)
    FUNCTION = "get_LoRAname_by_index"
    CATEGORY = "utils"

    def get_LoRAname_by_index(self, index, LoRAnames):
        # Split the LoRAnames into lines and remove empty lines
        LoRAname_lines = [line.strip() for line in LoRAnames.split('\n') if line.strip()]
        
        # Validate index
        if len(LoRAname_lines) == 0:
            print("No LoRAname provided. Returning empty string.")
            return ("",)
            
        if index < 0 or index >= len(LoRAname_lines):
            print(f"LoRAname index {index} out of range. Using default index 0.")
            index = 0 if len(LoRAname_lines) > 0 else -1
            
        if index == -1:
            return ("",)
            
        # Get the selected LoRAname
        selected_LoRAname = LoRAname_lines[index]
        print(f"Selected LoRAname at index {index}: '{selected_LoRAname}'")
                
        return (selected_LoRAname,)

NODE_CLASS_MAPPINGS = {
    "MultiLoRAnameLoader": MultiLoRAnameLoader
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "MultiLoRAnameLoader": "LoRAname (by Index)"
} 