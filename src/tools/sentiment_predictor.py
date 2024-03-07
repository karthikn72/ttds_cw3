from google.cloud import storage
import pandas as pd
from transformers import T5Tokenizer
from torch.utils.data import DataLoader
from t5_dataset import T5Dataset
from t5_finetuner import T5FineTuner
from tqdm.auto import tqdm
import os
import torch
import argparse

class SentimentPredictor():
    def __init__(self, class_name) -> None:
        self.model = None
        self.class_name = class_name
        self.keyfile_path = 'tools\sentinews-413116-89709afcbbd7.json'
        self.tokenizer = T5Tokenizer.from_pretrained('t5-base', model_max_length=512, truncation=True)

    def load_model(self):
        if not os.path.exists('sentiment_model'):
            storage_client = storage.Client.from_service_account_json(self.keyfile_path)
            
            bucket = storage_client.get_bucket('sentinews-articles')

            blob = bucket.get_blob('sent_model_t')

            print("Downloading pretrained model from cloud")

            with open('sentiment_model', 'wb') as f:
                with tqdm.wrapattr(f, "write", total=blob.size) as file_obj:
                    storage_client.download_blob_to_file(blob, file_obj)

        arg_dict = dict(
            model_name_or_path='t5-base',
            tokenizer_name_or_path='t5-base',
            max_seq_length=512,
            learning_rate=1e-4,
            weight_decay=0.0,
            adam_epsilon=1e-8,
            warmup_steps=0,
            train_batch_size=8,
            eval_batch_size=8,
            num_train_epochs=12,
            gradient_accumulation_steps=16,
            n_gpu=1,
            early_stop_callback=True,
            opt_level='O1',
            max_grad_norm=1.0,
            seed=42,
        )

        self.model = T5FineTuner(argparse.Namespace(**arg_dict), self.class_name)

        self.model.load_state_dict(torch.load('sentiment_model'))

        print("The model has been loaded successfully")


    def predict(self, text) -> str:
        skeleton = {
            'text': [],
            self.class_name: []
        }
        df = pd.DataFrame(skeleton)
        replacement = {'text': text, self.class_name: ""}
        df.loc[0] = replacement

        dataset = T5Dataset(self.class_name, self.tokenizer, df)
        loader = DataLoader(dataset, batch_size=32, shuffle=True)
        self.model.model.eval()
        attention = None
        for batch in loader:
            attention = self.model.model.generate(input_ids=batch['source_ids'], 
                                  attention_mask=batch['source_mask'], 
                                  max_length=2, output_scores=True, return_dict_in_generate=True)

        logits = attention['scores'][0]
        probabilities = torch.nn.functional.softmax(logits, dim=-1)

        sentiments = {}
        for id in [17141, 3617, 24972]:
            sentiments[self.tokenizer.decode(id)] = probabilities[0, id].item()

        return sentiments