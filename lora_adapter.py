import folder_paths

class LoRAStringAdapter:
    """Converts a string to a compatible LoRA input for the standard LoRA loader."""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "lora_name_string": ("STRING", {"default": ""}),
            }
        }

    RETURN_TYPES = (folder_paths.get_filename_list("loras"),)
    RETURN_NAMES = ("lora_name",)
    FUNCTION = "adapt_lora_name"
    CATEGORY = "utils"

    def adapt_lora_name(self, lora_name_string):
        available_loras = folder_paths.get_filename_list("loras")
        
        # If the string is empty or None, return a default
        if not lora_name_string:
            return (available_loras[0] if available_loras else "",)
            
        # If the requested LoRA exists in the list, return it
        if lora_name_string in available_loras:
            return (lora_name_string,)
            
        # Otherwise, provide a warning and return the first available LoRA
        print(f"Warning: LoRA '{lora_name_string}' not found in available LoRAs. Using first available LoRA.")
        return (available_loras[0] if available_loras else "",)

# Add the node to ComfyUI
NODE_CLASS_MAPPINGS = {
    "LoRAStringAdapter": LoRAStringAdapter
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LoRAStringAdapter": "LoRA String Adapter"
} 