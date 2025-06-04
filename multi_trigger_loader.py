import os
import re

class MultiTriggerLoader:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "index": ("INT", {"default": 0, "min": 0, "max": 99, "step": 1}),
                "triggers": ("STRING", {"multiline": True, "default": "trigger word 1\ntrigger word 2\ntrigger word 3"}),
            }
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "get_trigger_by_index"
    CATEGORY = "utils"

    def get_trigger_by_index(self, index, triggers):
        # Split the triggers into lines and remove empty lines
        trigger_lines = [line.strip() for line in triggers.split('\n') if line.strip()]
        
        # Validate index
        if len(trigger_lines) == 0:
            print("No trigger words provided. Returning empty string.")
            return ("",)
            
        if index == -1:
            return ("",)
        
        if index < 0 or index >= len(trigger_lines):
            print(f"Trigger index {index} out of range. Using default index 0.")
            index = 0
            
            
        # Get the selected trigger
        selected_trigger = trigger_lines[index]
        print(f"Selected trigger word at index {index}: '{selected_trigger}'")
                
        return (selected_trigger,)

# Add the node to ComfyUI
NODE_CLASS_MAPPINGS = {
    "MultiTriggerLoader": MultiTriggerLoader
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "MultiTriggerLoader": "Trigger Words (by Index)"
} 