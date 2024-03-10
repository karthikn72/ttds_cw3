
import nltk
from nltk.corpus import wordnet
from nltk.corpus import wordnet
import timer

class QueryExpander:
    def __init__(self):
        print("Downloading NLTK packages...")
        nltk.download('wordnet')
        nltk.download('averaged_perceptron_tagger')
        print("NLTK packages downloaded successfully.")


    def expand_query(self, query):  #assumed format of this is that it is a query before it is normalized and stopped, and stemmed and returns a list of tokens with the full token at the start
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
        index =0
        synonyms = []
        pos1 = nltk.pos_tag(query)
        for word in query:
            pos = _get_wordnet_pos(pos1[index])
            s = wordnet.synsets(word)
            for syn in s:
                if str(syn.pos()) == str(pos):
                    
                    for lemma in syn.lemmas():
                        similarity_score = wordnet.path_similarity(s[0], syn,)
                        #print(similarity_score, lemma.name(), s[0].name())
                        if (lemma.name() not in synonyms) and (similarity_score > 0.5):
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
        output = output.split()
        #remove original tokens from the list of synonyms
        for token in query:
            if token in output:
                output.remove(token)

        return output

if __name__ == '__main__':

    qe = QueryExpander()
    query = ['call', 'denver', 'direct']
    

    print(qe.expand_query(query))
    #['call', 'denver', 'direct', 'phone', 'telephone', 'cry', 'outcry', 'yell', 'shout', 'vociferation', 'claim', 'birdcall', 'birdsong', 'song', 'margin', 'option', 'mile', 'high', 'city', 'capital'] all syns
    query2 = ['python', 'programming', 'language']
    print(qe.expand_query(query2))
    #['python', 'programming', 'language', 'scheduling', 'programing', 'computer', 'linguistic', 'communication', 'speech', 'spoken', 'voice', 'oral', 'lyric', 'words', 'process', 'terminology', 'nomenclature'] all syns
    query3 = ['data', 'analysis', 'tools']
    print(qe.expand_query(query3))
    #['data', 'analysis', 'tools', 'information', 'datum', 'point', 'analytic', 'thinking', 'psychoanalysis', 'depth', 'psychology', 'tool', 'instrument', 'creature', 'puppet', 'cock', 'prick', 'dick', 'shaft', 'pecker', 'peter', 'putz'] all syns
    query4 = ['machine', 'learning', 'algorithms']
    print(qe.expand_query(query4))
    #['machine', 'learning', 'algorithms', 'simple', 'political', 'car', 'auto', 'automobile', 'motorcar', 'acquisition', 'eruditeness', 'erudition', 'learnedness', 'scholarship', 'encyclopedism', 'encyclopaedism', 'algorithm', 'algorithmic', 'rule', 'program'] all syns
    query5 = ['web', 'development', 'frameworks']
    print(qe.expand_query(query5))
    #['web', 'development', 'frameworks', 'entanglement', 'vane', 'network', 'world', 'wide', 'www', 'evolution', 'growth', 'growing', 'maturation', 'ontogeny', 'ontogenesis', 'exploitation', 'developing', 'model', 'theoretical', 'account', 'framework', 'fabric'] all syns