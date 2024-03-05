
import nltk
from nltk.corpus import wordnet
from tokenizer import Tokenizer, QueryTokenizer
from nltk.corpus import wordnet


class QueryExpander:
    
    
    
    
    
    
    def __init__(self):
        
        nltk.download('wordnet')
        nltk.download('average_perceptron_tagger')  

    def expand_query(self, untokenized_query):  #assumed format of this is that it is a query before it is normalized and stopped, and stemmed and returns a list of tokens with the full token at the start
        #this version of the query expander uses word pos tagging to get the synonyms of the words in the query
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
        if type(untokenized_query) == str:
            tokenizer = Tokenizer(stem=False, stop=True)
            query = tokenizer.tokenize(untokenized_query)
        else:
            query = untokenized_query
        
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
        #this can be removed depending on what we want the query expander to give back
        
        output += query
        for synonym in synonyms:
            this_count = count# avoids triple barreled words (why?)
            for word in synonym.split():
                if this_count > 0 and word not in output:
                    output.append(word)
                    this_count -= 1
        output = ' '.join(output)
        output = tokenizer.tokenize(output)


        return output
                
#notes to ask karthik 
    #1.what is the format of the query that is passed to the query expander
    #2. what is the format of the query that is returned by the query expander
    #3. how many synonyms do we want to add per word, how would we track this.

        
            


        

        

if __name__ == '__main__':
    
    qe = QueryExpander()
    query = 'call denver direct'
    print(qe.expand_query(query))
    #['call', 'denver', 'direct', 'phone', 'telephone', 'cry', 'outcry', 'yell', 'shout', 'vociferation', 'claim', 'birdcall', 'birdsong', 'song', 'margin', 'option', 'mile', 'high', 'city', 'capital']
    query2 = 'python programming language'
    print(qe.expand_query(query2))
    #['python', 'programming', 'language', 'scheduling', 'programing', 'computer', 'linguistic', 'communication', 'speech', 'spoken', 'voice', 'oral', 'lyric', 'words', 'process', 'terminology', 'nomenclature']
    query3 = 'data analysis tools'
    print(qe.expand_query(query3))
    #['data', 'analysis', 'tools', 'information', 'datum', 'point', 'analytic', 'thinking', 'psychoanalysis', 'depth', 'psychology', 'tool', 'instrument', 'creature', 'puppet', 'cock', 'prick', 'dick', 'shaft', 'pecker', 'peter', 'putz']
    query4 = 'machine learning algorithms'
    print(qe.expand_query(query4))
    #['machine', 'learning', 'algorithms', 'simple', 'political', 'car', 'auto', 'automobile', 'motorcar', 'acquisition', 'eruditeness', 'erudition', 'learnedness', 'scholarship', 'encyclopedism', 'encyclopaedism', 'algorithm', 'algorithmic', 'rule', 'program']
    query5 = 'web development frameworks'
    print(qe.expand_query(query5))
    #['web', 'development', 'frameworks', 'entanglement', 'vane', 'network', 'world', 'wide', 'www', 'evolution', 'growth', 'growing', 'maturation', 'ontogeny', 'ontogenesis', 'exploitation', 'developing', 'model', 'theoretical', 'account', 'framework', 'fabric']