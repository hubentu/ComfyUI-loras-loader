import os
import folder_paths

class DynamicLoRALoader:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "index": ("INT", {"default": 0, "min": 0, "max": 99, "step": 1}),
                "LoRAnames": ("STRING", {"multiline": True, "default": "LoRAname1.safetensors\nLoRAname2.safetensors\nLoRAname3.safetensors"}),
                "model": ("MODEL",),
                "strength_model": ("FLOAT", {"default": 1.0, "min": -10.0, "max": 10.0, "step": 0.01}),
                "strength_clip": ("FLOAT", {"default": 1.0, "min": -10.0, "max": 10.0, "step": 0.01}),
            },
            "optional": {
                "clip": ("CLIP",),
            }
        }

    RETURN_TYPES = ("MODEL", "CLIP")
    FUNCTION = "load_lora_by_index"
    CATEGORY = "loaders"

    def load_lora_by_index(self, index, LoRAnames, model, strength_model, strength_clip, clip=None):
        # Split the LoRAnames into lines and remove empty lines
        LoRAname_lines = [line.strip() for line in LoRAnames.split('\n') if line.strip()]
        
        # Validate index
        if len(LoRAname_lines) == 0:
            print("No LoRAname provided. Returning model without changes.")
            return (model, clip)
            
        if index < 0 or index >= len(LoRAname_lines):
            print(f"LoRAname index {index} out of range. Using default index 0.")
            index = 0 if len(LoRAname_lines) > 0 else -1
            
        if index == -1:
            return (model, clip)
            
        # Get the selected LoRAname
        selected_LoRAname = LoRAname_lines[index]
        print(f"Selected LoRAname at index {index}: '{selected_LoRAname}'")
        
        # Find the LoRA file in any of the lora directories
        lora_path = None
        lora_dirs = folder_paths.get_folder_paths("loras")
        
        for lora_dir in lora_dirs:
            potential_path = os.path.join(lora_dir, selected_LoRAname)
            if os.path.isfile(potential_path):
                lora_path = potential_path
                break
                
        # If we couldn't find the file
        if lora_path is None:
            print(f"LoRA file '{selected_LoRAname}' not found in any LoRA directories. Returning model without changes.")
            return (model, clip)
            
        print(f"Loading LoRA {selected_LoRAname} from {lora_path}")
        print(f"Model strength: {strength_model}, Clip strength: {strength_clip}")
        
        # Try to load the LoRA using ComfyUI's built-in LoRA loading functions
        try:
            # First try to import from comfy_extras
            import importlib
            
            # Try to find and use the built-in LoraLoader
            try:
                # Different ComfyUI versions store nodes in different places
                nodes_lora = None
                for module_name in ["comfy_extras.nodes_lora", "comfy.extra_model_paths", "nodes"]:
                    try:
                        nodes_lora = importlib.import_module(module_name)
                        if hasattr(nodes_lora, "LoraLoader"):
                            break
                    except ImportError:
                        continue
                
                if nodes_lora and hasattr(nodes_lora, "LoraLoader"):
                    lora_loader = nodes_lora.LoraLoader()
                    return lora_loader.load_lora(model, lora_path, strength_model, strength_clip, clip)
                else:
                    print("Could not find LoraLoader implementation, falling back to manual loading")
            except Exception as e:
                print(f"Error using ComfyUI's LoraLoader: {str(e)}")
            
            # If that fails, try direct loading method
            import comfy.utils
            import comfy.sd
            
            # Load the LoRA file
            lora_sd = comfy.utils.load_torch_file(lora_path)
            
            # Different versions of ComfyUI have different methods for applying LoRAs
            if hasattr(comfy.sd, "load_lora_for_models"):
                return comfy.sd.load_lora_for_models(model, clip, lora_sd, strength_model, strength_clip)
            elif hasattr(comfy.sd, "apply_lora"):
                model_out = model
                clip_out = clip
                if model is not None:
                    model_out = comfy.sd.apply_lora(model, lora_sd, strength_model)
                if clip is not None:
                    clip_out = comfy.sd.apply_lora(clip, lora_sd, strength_clip)
                return (model_out, clip_out)
            else:
                print("Could not find appropriate method to apply LoRA")
                
        except Exception as e:
            print(f"Error loading or applying LoRA: {str(e)}")
        
        # If all methods fail, return original model
        return (model, clip)

# Add the node to ComfyUI
NODE_CLASS_MAPPINGS = {
    "DynamicLoRALoader": DynamicLoRALoader
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "DynamicLoRALoader": "LoRA Loader (by Name Index)"
} 