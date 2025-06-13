import os
import re
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# Optional: change HF cache path (can remove if not needed)
os.environ["HF_HOME"] = r"C:\Users\prath\.cache\huggingface"

class TransformerCorrector:
    def __init__(self, model_name: str = "prithivida/grammar_error_correcter_v1"):
        print("Loading grammar correction model... (only once)")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

    def correct(self, text: str) -> str:
        inputs = self.tokenizer.encode(text, return_tensors="pt", max_length=512, truncation=True)
        outputs = self.model.generate(inputs, max_length=512, num_beams=5, early_stopping=True)
        corrected_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return corrected_text

# Lowercasing, punctuation cleanup
def clean_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s.,?!']", '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

# Initialize once globally
corrector = TransformerCorrector()

def preprocess(text: str) -> str:
    cleaned_text = clean_text(text)
    corrected_text = corrector.correct(cleaned_text)
    return corrected_text

# For direct testing
if __name__ == "__main__":
    sample_inputs = [
        "whne is the next elction in india?",
        "Tell me teh latest newz on war?",
        "is it tru that elon muskk bougt twiter"
    ]
    for q in sample_inputs:
        print(f"Original:    {q}")
        print(f"Preprocessed: {preprocess(q)}")
        print("-" * 50)
