import pandas as pd
#Task 1: create a function that returns a dataframe of the first 1000 documents in a dataset
def firstThousand(dataset_file):
    first1000 = []
    for chunk in pd.read_csv(dataset_file, chunksize=1000):
        first1000.append(chunk)
        break
    return pd.concat(first1000)


       
#Task 2: create a function that takes the sorted index and adds them to an index.txt

# additionally, the function should put the new posting in the right place alphabetically within the index
# and merge the postings if the word is already in the index
def output(filepath, postings, doc_count):

    with open('index.txt', 'w') as outFile:
        sorted_postings = dict(sorted(postings.items()))
        for word in sorted_postings.keys():
            outFile.write(f'{word}:{doc_count[word]}\n')
            for positions in sorted_postings[word]:
                outFile.write(' ' * 3 + positions)

    outFile.close()
                
    

    

        

            
#Task 3: create a function that takes a query term as an argument and returns the index for that word
def get_index(word): #returns array, first item is the word and the rest are the indexes
    with open('index.txt', 'r') as inFile:
        output = []
        token = False
        
        for line in inFile:
            
            if line.split(":")[0]==word and token == False:
                output.append(line[:-1])
                token = True
            elif line.startswith('   ') and token == True:

                output.append(line.strip())
            elif not line.startswith('   ') and token == True:
                
                return output

    
#code to test the functions
if __name__ == "__main__":
    dataset = "tools/dataset/all-the-news-2-1.csv"
    index = 'index.txt'
    index_add = 'index_test.txt'
    #create exact copy of index.txt



    data = firstThousand(dataset)
    print(data)
    data.to_csv('first1000.csv')
    output(index, postings, doc_count)

    print(get_index('00000'))
    print(get_index('design'))
