import os
import folder_paths
import torch

class MultiLoraLoader:
    # Class variable to store LoRA list
    all_loras = []
    
    @classmethod
    def INPUT_TYPES(cls):
        # Get all available lora directories and gather all lora files
        cls.all_loras = []
        lora_dirs = folder_paths.get_folder_paths("loras")
        
        for lora_dir in lora_dirs:
            if os.path.isdir(lora_dir):
                for filename in os.listdir(lora_dir):
                    if filename.endswith(('.safetensors', '.ckpt', '.pt')):
                        cls.all_loras.append(filename)
        
        # Sort and remove duplicates
        cls.all_loras = sorted(list(set(cls.all_loras)))
        
        # Print debug info
        print(f"Found {len(cls.all_loras)} LoRA files in {len(lora_dirs)} directories")
        
        max_index = max(0, len(cls.all_loras) - 1)
        
        return {
            "required": {
                "model": ("MODEL",),
                "index": ("INT", {"default": 0, "min": 0, "max": max_index, "step": 1}),
                "lora_list": (cls.all_loras, {"default": cls.all_loras[0] if cls.all_loras else ""}),
                "strength_model": ("FLOAT", {"default": 1.0, "min": -10.0, "max": 10.0, "step": 0.01}),
                "strength_clip": ("FLOAT", {"default": 1.0, "min": -10.0, "max": 10.0, "step": 0.01}),
            },
            "optional": {
                "clip": ("CLIP", ),
            }
        }

    RETURN_TYPES = ("MODEL", "CLIP")
    FUNCTION = "load_lora"
    CATEGORY = "loaders"

    def load_lora(self, model, index, lora_list, strength_model, strength_clip, clip=None):
        lora_dirs = folder_paths.get_folder_paths("loras")
        
        # Use the class variable to access the LoRA list
        all_loras = self.__class__.all_loras
        
        # Validate we have LoRAs and index is in range
        if len(all_loras) == 0:
            print("No LoRAs found. Returning model without changes.")
            return (model, clip)
            
        if index < 0 or index >= len(all_loras):
            print(f"LoRA index {index} out of range (0-{len(all_loras)-1}). Using index 0.")
            index = 0
        
        # Get the LoRA file name based on index
        lora_name = all_loras[index]
        
        # Find the LoRA file in any of the lora directories
        lora_path = None
        for lora_dir in lora_dirs:
            potential_path = os.path.join(lora_dir, lora_name)
            if os.path.isfile(potential_path):
                lora_path = potential_path
                break
                
        # If we couldn't find the file
        if lora_path is None:
            print(f"LoRA file '{lora_name}' not found in any LoRA directories. Returning model without changes.")
            return (model, clip)
            
        print(f"Loading LoRA {lora_name} (index {index}/{len(all_loras)-1}) from {lora_path}")
        print(f"Model strength: {strength_model}, Clip strength: {strength_clip}")
        
        # Import the reference implementation from ComfyUI's nodes
        try:
            import importlib.util
            import sys
            
            # Get the ComfyUI nodes directory
            script_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
            comfy_dir = os.path.join(script_dir, "comfy")
            nodes_dir = os.path.join(script_dir, "comfy_extras")
            
            if os.path.exists(os.path.join(comfy_dir, "sd.py")) and os.path.exists(os.path.join(nodes_dir, "nodes_lora.py")):
                # Load the lora module directly from ComfyUI
                spec = importlib.util.spec_from_file_location("nodes_lora", os.path.join(nodes_dir, "nodes_lora.py"))
                nodes_lora = importlib.util.module_from_spec(spec)
                sys.modules["nodes_lora"] = nodes_lora
                spec.loader.exec_module(nodes_lora)
                
                # Use the reference implementation
                lora_loader = nodes_lora.LoraLoader()
                return lora_loader.load_lora(model, lora_path, strength_model, strength_clip, clip)
            else:
                print("Could not find ComfyUI's nodes_lora.py, falling back to internal implementation")
                
        except Exception as e:
            print(f"Error loading ComfyUI's LoraLoader: {str(e)}")
        
        # If we couldn't use the reference implementation, use our own
        try:
            import comfy.utils
            
            # Load the LoRA file
            lora_sd = comfy.utils.load_torch_file(lora_path)
            
            # We need to import these from comfy's sd module
            import comfy.sd as sd
            
            # Apply the LoRA
            if hasattr(sd, 'load_lora_for_models'):
                return sd.load_lora_for_models(model, clip, lora_sd, strength_model, strength_clip)
            else:
                model_result = model
                clip_result = clip
                
                if hasattr(sd, 'apply_weighted_lora'):
                    # Newer ComfyUI versions
                    if model is not None:
                        model_result = sd.apply_weighted_lora(model, lora_sd, strength_model)
                    if clip is not None:
                        clip_result = sd.apply_weighted_lora(clip, lora_sd, strength_clip)
                elif hasattr(sd, 'apply_lora'):
                    # Older ComfyUI versions
                    if model is not None:
                        model_result = sd.apply_lora(model, lora_sd, strength_model)
                    if clip is not None:
                        clip_result = sd.apply_lora(clip, lora_sd, strength_clip)
                else:
                    print("Could not find apply_lora or apply_weighted_lora in ComfyUI's sd module")
                
                return (model_result, clip_result)
                
        except Exception as e:
            print(f"Error loading or applying LoRA: {str(e)}")
            
        # If all else fails, return the original models
        print("All LoRA loading methods failed, returning original model")
        return (model, clip)

# Add the node to ComfyUI
NODE_CLASS_MAPPINGS = {
    "MultiLoraLoader": MultiLoraLoader
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "MultiLoraLoader": "LoRA Loader (by Index)"
} 