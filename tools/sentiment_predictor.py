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

        print(sentiments)

        return sentiments
    

if __name__ == "__main__":
    sentP = SentimentPredictor("predicted_class")
    sentP.load_model()
    sentP.predict("""Puerto Rico relaxes COVID curfew, reopens beaches but bans alcohol in certain public spaces
SAN JUAN, Puerto Rico – Puerto Rico’s new governor announced Tuesday that he will reopen beaches, marinas and pools, eliminate a Sunday lockdown and shorten a curfew that has been in place since the pandemic began to control the number of COVID-19 cases.

Gov. Pedro Pierluisi stressed alcohol will be banned at beaches and other places, and that social distancing is required between people who are not family members, with no large groups allowed to gather. Meanwhile, the new curfew will run from 11 p.m. to 5 a.m. and face masks remain mandatory.

The new measures took effect Thursday and will be in place for 30 days but can be amended any time if there’s a spike in cases.

The announcement was cheered by many across Puerto Rico who have long sought to visit the U.S. territory’s beaches that had remained off limits to all except those doing exercise.

He also ordered Puerto Rico’s Treasury Department to use federal funds and create economic incentives to help tens of thousands of small and medium businesses hard hit by strict closures that have been in place since March.

The U.S. territory of 3.2 million people has reported more than 127,000 confirmed and probable cases and more than 1,200 confirmed deaths.

Pierluisi kept in place other measures implemented by former Gov. Wanda Vázquez, including the closure of bars and a limited capacity at gyms, restaurants and other places.

“Our goal has to be to be able to return to a new normal,” Pierluisi said. “We have to keep taking preventive measures in the meantime.”

The announcement comes the same day that health experts began receiving the second COVID-19 vaccine dose, with some 60,000 people vaccinated so far and an expected 90,000 by the end of the week. Those scheduled to be vaccinated soon include teachers, with Pierluisi saying in-person classes could resume by March on a gradual scale.

Carlos Mellado, Puerto Rico’s designated health secretary, said he expects 40,000 vaccine doses to arrive on the island every week.

Meanwhile, officials reported an outbreak at a prison in the northern city of Bayamon, with more than 140 inmates testing positive. Nearly all are asymptomatic, but two have been hospitalized. Officials said the outbreak began when a corrections officer who had COVID-19 came into contact with five inmates.""")