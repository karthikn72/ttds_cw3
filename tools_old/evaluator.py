from retrieval import TFIDFScoring
from tokenizer import QueryTokenizer
import numpy as np

class Evaluator:
    def __init__(self) -> None:
        self.scores = None
        self.retrieved = None
        self.tokenizer = QueryTokenizer()
        self.retrieval = TFIDFScoring()
    
    def setup(self, query):
        # This method should instantiate the relevance scoring and the actual retrieved results
        self.scores = self.retrieval.score(self.tokenizer.tokenize(query))
        self.retrieved = None
    
    def k_precision(self, k=10):
        tp = 0
        relevant_docs = [s[0] for s in self.scores]

        for i in range(k):
            if self.retrieved[i] in relevant_docs:
                tp += 1
        return tp / k
    
    def k_recall(self, k):
        tp = 0
        relevant_docs = [s[0] for s in self.scores]
        for i in range(k):
            if self.retrieved[i] in relevant_docs:
                tp += 1
        return tp / len(relevant_docs)
    
    def r_precision(self):
        self.k_precision(len(self.scores))

    def average_precision(self):
        count = 0
        idx = 1
        score = 0
        relevant_docs = [s[0] for s in self.scores]
        
        while count < len(self.scores) and idx <= len(self.retrieved):
            if self.retrieved[idx - 1] in relevant_docs:
                count += 1
                score += count / idx
            idx += 1

        return score / len(self.scores)
    
    def calculate_idcg(self, k):
        score = self.scores[0][1]

        for i in range(2, min(k + 1, len(self.scores) + 1)):
            score += self.scores[i - 1][1] / np.log2(i)

        return score
    
    def find_relevance(self, doc_num):
        for doc, rel in self.scores:
            if doc == doc_num:
                return rel
            
    def calculate_dcg(self, k):
        if len(self.retrieved) == 0:
            return 0
        
        score = 0
        relevant_docs = [s[0] for s in self.scores]
        if self.retrieved[0] in relevant_docs:
            score = self.find_relevance(self.retrieved[0])
        
        for i in range(2, min(k + 1, len(self.retrieved) + 1)):
            if self.retrieved[i-1] in relevant_docs:
                score += self.find_relevance(self.retrieved[i-1]) / np.log2(i)

        return score
    
    def calculate_ndcg(self, k):
        return self.calculate_dcg(k) / self.calculate_idcg(k)

    def evaluate(self):
        # calling various evaluation metrics
        pass


if __name__ == '__main__':
    evaluator = Evaluator()

    query = "us president election"

    print(evaluator.evaluate(query))