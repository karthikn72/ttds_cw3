from t5_dataset import T5Dataset 

import torch
from torch.utils.data import Dataset, DataLoader, RandomSampler
import pytorch_lightning as pl
from transformers import (
    T5ForConditionalGeneration,
    T5Tokenizer,
    get_linear_schedule_with_warmup
)

class T5FineTuner(pl.LightningModule):
    def __init__(self, hparams, class_name, sampler = None):
        super(T5FineTuner, self).__init__()
        self.sampler = sampler
        self.save_hyperparameters(hparams)
        self.training_step_outputs = []
        self.validation_step_outputs = []
        # self.dataset = T5Dataset(class_name)

        self.model = T5ForConditionalGeneration.from_pretrained(self.hparams.model_name_or_path)
        self.tokenizer = T5Tokenizer.from_pretrained(self.hparams.tokenizer_name_or_path)

    def forward(
        self, input_ids, attention_mask=None, decoder_input_ids=None, decoder_attention_mask=None, labels=None
    ):
        return self.model(
            input_ids,
            attention_mask=attention_mask,
            decoder_input_ids=decoder_input_ids,
            decoder_attention_mask=decoder_attention_mask,
            labels=labels
        )

    def _step(self, batch):
        labels = batch["target_ids"]
        labels[labels[:, :] == self.tokenizer.pad_token_id] = -100

        outputs = self(
            input_ids=batch["source_ids"],
            attention_mask=batch["source_mask"],
            labels=labels,
            decoder_attention_mask=batch['target_mask']
        )

        loss = outputs[0]

        return loss

    def training_step(self, batch, batch_idx):
        loss = self._step(batch)

        return loss
        
    def on_train_epoch_end(self):
        self.training_step_outputs.clear() 

    def validation_step(self, batch, batch_idx):
        loss = self._step(batch)

        return loss
        
    def on_validation_epoch_end(self):
        self.validation_step_outputs.clear()  # free memory

    def configure_optimizers(self):
        "Prepare optimizer and schedule (linear warmup and decay)"

        model = self.model
        no_decay = ["bias", "LayerNorm.weight"]
        optimizer_grouped_parameters = [
            {
                "params": [p for n, p in model.named_parameters() if not any(nd in n for nd in no_decay)],
                "weight_decay": self.hparams.weight_decay,
            },
            {
                "params": [p for n, p in model.named_parameters() if any(nd in n for nd in no_decay)],
                "weight_decay": 0.0,
            },
        ]
        optimizer = torch.optim.AdamW(optimizer_grouped_parameters, lr=self.hparams.learning_rate, eps=self.hparams.adam_epsilon)
        self.opt = optimizer
        return [optimizer]

    def optimizer_step(
        self,
        epoch,
        batch_idx,
        optimizer,
        optimizer_closure,
        ):
        optimizer = optimizer.optimizer
        optimizer.step(closure=optimizer_closure)