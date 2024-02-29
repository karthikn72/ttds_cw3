import pickle
import pandas as pd
from indexer import Indexer
from retrieval_2 import Retrieval
import time

#Task 1: create a function that returns a dataframe of the first 1000 documents in a dataset
def firstThousand(dataset_file):
    first1000 = pd.read_csv(dataset_file, nrows=1000)
    second1000 = pd.read_csv(dataset_file, skiprows=1000, nrows=1000)
    return first1000, second1000
       
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
    dataset = "../tools/dataset/all-the-news-2-1.csv"
    dataset, dataset2 = firstThousand(dataset)
    print(dataset.head())
    print(dataset2.head())
    #write in the same dataset folder
    dataset.to_csv("first1000.csv", index=True)
    
    start_time = time.time()
    idxer = Indexer()
    end_time = time.time()
    print(f"Time taken to initialise idxer: {end_time - start_time:.10f} seconds")
    start_time = time.time()
    idxer.set_up_stopwords("../tools/resources/ttds_2023_english_stop_words.txt")
    end_time = time.time()
    print(f"Time taken to set up stopwords: {end_time - start_time:.10f} seconds")
    start_time = time.time()
    idxer.indexing("../tools/first1000.csv") #change
    end_time = time.time()
    print(f"Time taken to index the first 1000 documents using Indexer: {end_time - start_time:.10f} seconds")
    # testing time for just opening pkl file
    start_time = time.time()
    with open('index_tfidf.pkl', 'rb') as f:
        new = pickle.load(f)
    end_time = time.time()
    print(f"Time taken to unpickle the pickle: {end_time - start_time:.10f} seconds")

    #retrieval tests
    start_time = time.time()
    ret = Retrieval()  
    end_time = time.time()
    print(f"Time taken to initialise retrieval: {end_time - start_time:.10f} seconds") 
    start_time = time.time()
    design=ret.get_index('design')
    end_time = time.time()
    print(f"Time taken to get index for 'design': {end_time - start_time:.10f} seconds")
    start_time = time.time()
    ret.get_query_score("against all logic")
    end_time = time.time()
    print(f"Time taken to get tfidf for 'against all logic': {end_time - start_time:.10f} seconds")    #this is not correct 
# Time taken to initialise idxer: 1.3113021850585938e-05 seconds
# Time taken to set up stopwords: 0.00033783912658691406 seconds
# Time taken to index the first 1000 documents using Indexer: 6.981287956237793 seconds
# Time taken to unpickle the pickle: 0.5805950164794922 seconds
# Time taken to initialise retrieval: 0.8500440120697021 seconds
# Time taken to get index for 'design': 5.1975250244140625e-05 seconds
# Time taken to get tfidf for 'against all logic': 0.0017879009246826172 seconds
    idxer.indexing("first1000.csv",'txt') 
    idxer.indexing("first1000.csv",'dbs')
    #print some of the database from words.db to show how it works
    import sqlite3
    conn = sqlite3.connect('words.db')
    c = conn.cursor()
    c.execute('SELECT * FROM words')
    print(c.fetchmany(10))
    c.execute('SELECT * FROM documents')
    print(c.fetchmany(10))
    c.execute('SELECT * FROM wordindoc')
    print(c.fetchmany(10))


    

