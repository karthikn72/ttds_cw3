from torch.utils.data import Dataset

class T5Dataset(Dataset):
  def __init__(self, tokenizer, data, column_name, max_len=512):
    self.data_column = "text"
    self.class_column = column_name
    self.data = data

    self.max_len = max_len
    self.tokenizer = tokenizer
    self.inputs = []
    self.targets = []

    self._build()

  def __len__(self):
    return len(self.inputs)

  def __getitem__(self, index):
    source_ids = self.inputs[index]["input_ids"].squeeze()
    target_ids = self.targets[index]["input_ids"].squeeze()

    src_mask    = self.inputs[index]["attention_mask"].squeeze() 
    target_mask = self.targets[index]["attention_mask"].squeeze()  

    return {"source_ids": source_ids, "source_mask": src_mask, "target_ids": target_ids, "target_mask": target_mask}

  def _build(self):
    for idx in range(len(self.data)):
        input_, target = self.data.loc[idx, self.data_column], self.data.loc[idx, self.class_column]

        # tokenize inputs
        tokenized_inputs = self.tokenizer.batch_encode_plus(
            [input_], max_length=self.max_len, padding='max_length', return_tensors="pt", truncation=True, add_special_tokens=True
        )
        # tokenize targets
        tokenized_targets = self.tokenizer.batch_encode_plus(
            [target], max_length=8, padding='max_length', return_tensors="pt", truncation=True, add_special_tokens=True
        )

        self.inputs.append(tokenized_inputs)
        self.targets.append(tokenized_targets)