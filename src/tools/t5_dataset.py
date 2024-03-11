from torch.utils.data import Dataset

class T5Dataset(Dataset):
  def __init__(self, column_name, tokenizer = None, data=None, max_len=512):
    self.data_column = "text"
    self.class_column = column_name
    self.data = data

    self.max_len = max_len
    self.tokenizer = tokenizer
    self.inputs = []

    self._build()

  def __len__(self):
    return len(self.inputs)

  def __getitem__(self, index):
    source_ids = self.inputs[index]["input_ids"].squeeze()

    src_mask = self.inputs[index]["attention_mask"].squeeze() 

    return {"source_ids": source_ids, "source_mask": src_mask}

  def _build(self):
    for idx in range(len(self.data)):
        input_ = self.data.loc[idx, self.data_column]

        # tokenize inputs
        tokenized_inputs = self.tokenizer.batch_encode_plus(
            [input_], max_length=self.max_len, padding='max_length', return_tensors="pt", truncation=True, add_special_tokens=True
        )

        self.inputs.append(tokenized_inputs)