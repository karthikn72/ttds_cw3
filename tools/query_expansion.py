
import nltk
from nltk.corpus import wordnet

class QueryExpander:
    nltk.download('wordnet')
    def __init__(self):
        self.expansion_query_terms = set()

    def expand_query(self, query):
        for word in query.split():
            self.expansion_query_terms.add(word)
            for syn in wordnet.synsets(word):
                for lemma in syn.lemmas():
                    self.expansion_query_terms.add(lemma.name())
        return ' '.join(self.expansion_query_terms)
        

if __name__ == '__main__':
    
    qe = QueryExpander()
    query = 'call denver direct'
    print(qe.expand_query(query))
