import pickle
import pandas as pd
from indexer import Indexer
from retrieval import Retrieval
import time

#Task 1: create a function that returns a dataframe of the first 1000 documents in a dataset
def firstThousand(dataset_file):
    first1000 = pd.read_csv(dataset_file, nrows=1000)
    return first1000
       
#Task 2: create a function that takes the sorted index and adds them to an index.txt

# additionally, the function should put the new posting in the right place alphabetically within the index
# and merge the postings if the word is already in the index (this one is functionally obsolete)
def output(filepath, postings, doc_count):
    with open('index.txt', 'w') as outFile:
        sorted_postings = dict(sorted(postings.items()))
        for word in sorted_postings.keys():
            outFile.write(f'{word}:{doc_count[word]}\n')
            for positions in sorted_postings[word]:
                outFile.write(' ' * 3 + positions)

    outFile.close()   

            
#Task 3: create a function that takes a query term as an argument and returns the index for that word
def get_index(word, index_path): #path is now a .pkl file
    output ={}
    with open(index_path, 'rb') as f:
        data = pickle.load(f)
        for doc in data[word]['indexes']:
            output[doc] = data[word]['indexes'][doc]['positions']
    return output

    
#code to test the functions
if __name__ == "__main__":
    dataset = "dataset/all-the-news-2-1.csv"
    start_time = time.time()
    idxer = Indexer()
    end_time = time.time()
    print("Time taken to initialise idxer:", end_time - start_time, "seconds")
    start_time = time.time()
    idxer.set_up_stopwords("../tools/resources/ttds_2023_english_stop_words.txt")
    end_time = time.time()
    print("Time taken to set up stopwords:", end_time - start_time, "seconds")
    start_time = time.time()
    idxer.indexing("../tools/first1000.csv") #change
    end_time = time.time()
    print("Time taken to index the first 1000 documents using Indexer:", end_time - start_time, "seconds")
    # testing time for just opening pkl file
    start_time = time.time()
    with open('index_tfidf.pkl', 'rb') as f:
        new = pickle.load(f)
    end_time = time.time()
    print("Time taken to unpickle the pickle:", end_time - start_time, "seconds")

    #retrieval tests
    start_time = time.time()
    ret = Retrieval()  
    end_time = time.time()
    print("Time taken to initialise retrieval:", end_time - start_time, "seconds") 
    start_time = time.time()
    design=ret.get_index('design')
    end_time = time.time()
    print("Time taken to get index for 'design':", end_time - start_time, "seconds")
    start_time = time.time()
    ret.get_query_score("against all logic")
    end_time = time.time()
    print("Time taken to get tfidf for 'against all logic':", end_time - start_time, "seconds")    


    # postings = {}
    # doc_count = {}
    # output(index, postings, doc_count)

    # print(get_index('00000',index))
    # print(get_index('design',index))

