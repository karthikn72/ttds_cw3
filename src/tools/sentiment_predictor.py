from google.cloud import storage
import pickle
import pandas as pd
from transformers import T5Tokenizer
from torch.utils.data import DataLoader
from t5_dataset import T5Dataset
from t5_finetuner import T5FineTuner
from tqdm.auto import tqdm
import os
import torch

class SentimentPredictor():
    def __init__(self, class_name) -> None:
        self.model = None
        self.class_name = class_name
        self.keyfile_path = 'tools\sentinews-413116-89709afcbbd7.json'
        self.tokenizer = T5Tokenizer.from_pretrained('t5-base', model_max_length=512, truncation=True)

    def load_model(self):
        if not os.path.exists('ml_models\sentiment.pkl'):
            storage_client = storage.Client.from_service_account_json(self.keyfile_path)
            
            bucket = storage_client.get_bucket('sentinews-articles')

            blob = bucket.get_blob('sentiment.pkl')

            print("Downloading pretrained model from cloud")

            with open('ml_models\sentiment.pkl', 'wb') as f:
                with tqdm.wrapattr(f, "write", total=blob.size) as file_obj:
                    storage_client.download_blob_to_file(blob, file_obj)

        with open('ml_models\sentiment.pkl', 'rb') as file:
            self.model = pickle.load(file)

        print("The model has been loaded successfully")


    def predict(self, text) -> str:
        def take_substring_until_char(input_string, target_char):
            index = input_string.find(target_char)
            if index != -1:
                substring = input_string[:index]
                return substring
            else:
                return input_string
            
        skeleton = {
            'text': [],
            self.class_name: []
        }
        df = pd.DataFrame(skeleton)
        replacement = {'text': text, self.class_name: ""}
        df.loc[0] = replacement

        dataset = T5Dataset(self.tokenizer, df, self.class_name)
        loader = DataLoader(dataset, batch_size=32, shuffle=True)
        self.model.cuda()
        self.model.model.eval()
        attention = None
        for batch in loader:
            attention = self.model.model.generate(input_ids=batch['source_ids'].cuda(), 
                                  attention_mask=batch['source_mask'].cuda(), 
                                  max_length=2, output_scores=True, return_dict_in_generate=True)

        logits = attention['scores'][0]
        probabilities = torch.nn.functional.softmax(logits, dim=-1)

        sentiments = {}
        for id in [17141, 3617, 24972]:
            sentiments[self.tokenizer.decode(id)] = probabilities[0, id].item()

        return sentiments