"""
Custom EndpointHandler for Vertex AI model deployment.
This handler loads the fine-tuned Phi-3 model and processes inference requests.
"""
import os
import re
import torch
from typing import Dict, List, Any
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel


# Model directory - will be set to /mnt/models when running in Vertex AI container
# For local testing, download the model from GCS to a local directory
MODEL_DIR = os.getenv("AIP_STORAGE_URI", "/mnt/models")


class EndpointHandler:
    """Handler for processing inference requests using a fine-tuned Hugging Face model."""

    def __init__(self, model_dir: str = MODEL_DIR) -> None:
        """
        Load tokenizer and model from the specified directory.
        
        Args:
            model_dir: Path to the directory containing the model artifacts
        """
        print(f"🔧 Initializing EndpointHandler with model_dir: {model_dir}")
        
        # Load tokenizer
        print("📝 Loading tokenizer...")
        self.tokenizer = AutoTokenizer.from_pretrained(
            model_dir,
            trust_remote_code=True
        )
        self.tokenizer.pad_token = self.tokenizer.eos_token
        self.tokenizer.padding_side = "right"
        
        # Determine device
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"💻 Using device: {self.device}")
        
        # Load model
        print("🤖 Loading model...")
        self.model = AutoModelForCausalLM.from_pretrained(
            model_dir,
            device_map="auto" if torch.cuda.is_available() else None,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            trust_remote_code=True,
        )
        
        # Set model to evaluation mode
        self.model.eval()
        print("✅ Model loaded successfully!")
        
    def __call__(self, data: Dict[str, Any]) -> Dict[str, List[Dict[str, str]]]:
        """
        Process inference requests in Vertex AI prediction format.
        
        Input format:
        {
            "instances": [
                {
                    "prompt": "user's message text"
                }
            ],
            "parameters": {
                "max_new_tokens": 256,
                "temperature": 0.7,
                "top_p": 0.9,
                "do_sample": true
            }
        }
        
        Output format:
        {
            "predictions": [
                {
                    "generated_text": "model's response"
                }
            ]
        }
        
        Args:
            data: Dictionary containing 'instances' and optional 'parameters'
            
        Returns:
            Dictionary containing 'predictions' list
        """
        # Extract instances and parameters
        instances = data.get("instances", [])
        parameters = data.get("parameters", {})
        
        if not instances:
            return {"predictions": [{"error": "No instances provided"}]}
        
        # Default generation parameters
        generation_params = {
            "max_new_tokens": parameters.get("max_new_tokens", 256),
            "temperature": parameters.get("temperature", 0.7),
            "top_p": parameters.get("top_p", 0.9),
            "do_sample": parameters.get("do_sample", True),
            "pad_token_id": self.tokenizer.eos_token_id,
        }
        
        predictions = []
        
        for instance in instances:
            prompt = instance.get("prompt", "")
            
            if not prompt:
                predictions.append({"error": "Empty prompt"})
                continue
            
            try:
                # Apply chat template
                messages = [{"role": "user", "content": prompt}]
                formatted_prompt = self.tokenizer.apply_chat_template(
                    messages,
                    tokenize=False,
                    add_generation_prompt=True
                )
                
                # Tokenize input
                inputs = self.tokenizer(
                    formatted_prompt,
                    return_tensors="pt",
                    padding=True,
                    truncation=True,
                    max_length=512
                ).to(self.device)
                
                # Generate response
                with torch.no_grad():
                    outputs = self.model.generate(
                        **inputs,
                        **generation_params
                    )
                
                # Decode the generated text
                generated_text = self.tokenizer.decode(
                    outputs[0],
                    skip_special_tokens=False
                )
                
                # Extract only the assistant's response
                response = self._extract_response(generated_text)
                
                predictions.append({"generated_text": response})
                
            except Exception as e:
                print(f"❌ Error processing instance: {e}")
                predictions.append({"error": str(e)})
        
        return {"predictions": predictions}
    
    def _extract_response(self, generated_text: str) -> str:
        """
        Extract the assistant's response from the generated text.
        
        Args:
            generated_text: Full generated text including prompt and special tokens
            
        Returns:
            Extracted assistant response
        """
        # Try to extract text after <|assistant|> token
        assistant_pattern = r"<\|assistant\|>\s*(.*?)(?:<\|end\||$)"
        match = re.search(assistant_pattern, generated_text, re.DOTALL)
        
        if match:
            response = match.group(1).strip()
            return response
        
        # Fallback: return the text after the last occurrence of the prompt
        # This is a simple heuristic
        return generated_text.split("<|assistant|>")[-1].strip() if "<|assistant|>" in generated_text else generated_text


# For local testing
if __name__ == "__main__":
    print("🧪 Testing EndpointHandler locally...")
    
    # For local testing, set this to your local model directory
    # Download model from GCS first: 
    # gsutil -m cp -r gs://llmops_101_europ/pipeline_root/.../fine_tuned_model ./local_model
    local_model_dir = os.getenv("LOCAL_MODEL_DIR", "./local_model")
    
    if not os.path.exists(local_model_dir):
        print(f"❌ Local model directory not found: {local_model_dir}")
        print("Please download the model from GCS first:")
        print("gsutil -m cp -r gs://llmops_101_europ/pipeline_root/432566588992/nutrition-assistant-training-pipeline-20251021140422/fine-tuning-component_-346527857045929984/fine_tuned_model ./local_model")
        exit(1)
    
    # Initialize handler
    handler = EndpointHandler(model_dir=local_model_dir)
    
    # Test with sample data
    test_data = {
        "instances": [
            {"prompt": "What are the nutritional benefits of spinach?"}
        ],
        "parameters": {
            "max_new_tokens": 150,
            "temperature": 0.7
        }
    }
    
    print("\n📤 Sending test request...")
    result = handler(test_data)
    
    print("\n📥 Response:")
    print(result)
