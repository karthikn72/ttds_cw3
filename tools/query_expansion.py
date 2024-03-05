
import nltk
from nltk.corpus import wordnet
from tokenizer import Tokenizer, QueryTokenizer
from nltk.corpus import wordnet


class QueryExpander:
    
    
    
    
    
    
    def __init__(self):
        
        nltk.download('wordnet')
        nltk.download('average_perceptron_tagger')  

    def expand_query(self, untokenized_query):  #assumed format of this is that it is a query before it is normalized and stopped, and stemmed and returns a list of tokens with the full token at the start
        def _get_wordnet_pos(tag:str) -> str:

            if tag[1].startswith('J'):
                return wordnet.ADJ
            elif tag[1].startswith('N'):
                return wordnet.NOUN
            elif tag[1].startswith('R'):
                return wordnet.ADV
            elif tag[1].startswith('V'):
                return wordnet.VERB
            else: return ''
        
        #this one assumes a non_tokenized query
        #detect if the query is a list or a string
        if type(untokenized_query) == SyntaxWarning:
            tokenizer = Tokenizer(stem=False, stop=True)
            query = tokenizer.tokenize(untokenized_query)
        
        index =0
        synonyms = []
        
        
        pos1 = nltk.pos_tag(query)


        for word in query:
            pos = _get_wordnet_pos(pos1[index])
            for syn in wordnet.synsets(word):
                if str(syn.pos()) == str(pos):
                    
                    for lemma in syn.lemmas():
                        if lemma.name() not in synonyms:
                            synonyms.append(lemma.name())
            index+=1
       
        clean_synonyms = []
        for word in synonyms:
            if '_' in word:
               
                
                clean_synonyms.append(word.lower().replace('_',' '))
            else:
                clean_synonyms.append(word.lower())

        synonyms = clean_synonyms
        output = []
        count = 2 #maximum number of synonyms to add per word
        output += [untokenized_query]
        
        output += query
        for synonym in synonyms:
            this_count = count# avoids triple barreled words (why?)
            for word in synonym.split():
                if this_count > 0 and word not in output:
                    output.append(word)
                    this_count -= 1
        return output
                

        
            
        

#current caveats:
            #TODO:figure out why the tokeniser returns a tuple #DONE
            #TODO:LIMIT THE ADDITIONS TO 2 PER WORD  DONE
            #TODO:FIGURE OUT HOW TO DEAL WITH SYNONYMS WITH SPACES DONE
            #TODO: FIGURE OUT WHATS NOT WORKING WITH THE TOKENISER SPELLCHECKER 
            #TODO: FIGURE OUT HOW TO DEAL WITH DOUBLE-TRIPLE BARREL TERMS ???
        

        

if __name__ == '__main__':
    
    qe = QueryExpander()
    query = 'call denver direct'
    print(qe.expand_query2(query))
    query2 = 'python programming language'
    print(qe.expand_query2(query2))
    
    query3 = 'data analysis tools'
    print(qe.expand_query2(query3))
    
    query4 = 'machine learning algorithms'
    print(qe.expand_query2(query4))
    
    query5 = 'web development frameworks'
    print(qe.expand_query2(query5))
