from transformers import ConvNextFeatureExtractor, ConvNextModel
import torch
from datasets import load_dataset

dataset = load_dataset("huggingface/cats-image")
image = dataset["test"]["image"][0]

feature_extractor = ConvNextFeatureExtractor.from_pretrained("facebook/convnext-tiny-224")
model = ConvNextModel.from_pretrained("facebook/convnext-tiny-224")

inputs = feature_extractor(image, return_tensors="pt")

with torch.no_grad():
    outputs = model(**inputs)


last_hidden_states = outputs.pooler_output
print(last_hidden_states.shape)