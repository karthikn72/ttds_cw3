import pandas as pd
#Task 1: create a function that returns a dataframe of the first 1000 documents in a dataset
def firstThousand(dataset_file):
    first1000 = []
    for chunk in pd.read_csv(dataset, chunksize=1000):
        first1000.append(chunk)
        break
    return pd.concat(first1000)


       
#Task 2: create a function that takes the sorted index and adds them to an index.txt

# additionally, the function should put the new posting in the right place alphabetically within the index
# and merge the postings if the word is already in the index
def add_to_index(filepath, sorted_postings_file):
    with open(filepath, 'r') as file1:
        data1 = file1.read().splitlines()
    with open(sorted_postings_file, 'r') as file2:
        data2 = file2.read().splitlines()
    i,j = 0,0
    merged = []
    while i < len(data1) and j < len(data2):
        if data1[i].split(':')[0] < data2[j].split(':')[0]:
            merged.append(data1[i])
            i += 1
            while i < len(data1):
                if data1[i].startswith('   '):
                    merged.append(data1[i])
                    i += 1
                else:
                    break
        elif data1[i].split(':')[0] == data2[j].split(':')[0]:
            word = data1[i].split(':')[0]
            i += 1
            j += 1
            """# if the docs are always different
            count = int(data1[i].split(':')[1]) + int(data2[j].split(':')[1])
            merged.append(f'{word}:{count}')
            while not data1[i].startswith('   ') and not data2[j].startswith('   '):
                if data1[i]< data2[j]:
                    merged.append(data1[i])
                    i += 1
                else:
                    merged.append(data2[j])
                    j += 1
            while true:
                if data1[i].startswith('   '):
                    merged.append(data1[i])
                    i += 1
                else:
                    break
            while true:
                if data2[j].startswith('   '):
                    merged.append(data2[j])
                    j += 1
                else:
                    break
            """
            #if the docs can be the same
            dict1 = {}
            while i < len(data1) and j < len(data2):
                if data1[i].startswith('   ') and data2[j].startswith('   '):
                    if data1[i].split(':')[0] < data2[j].split(':')[0]:
                        doc = data1[i][3:].split(':')[0]
                        positions = [int(pos) for pos in data1[i][3:].split(':')[1].split(',')]
                        dict1[doc] = positions
                        i += 1
                    elif data1[i].split(':')[0] == data2[j].split(':')[0]:
                        doc = data1[i][3:].split(':')[0]
                        positions1 = [int(pos) for pos in data1[i][3:].split(':')[1].split(',')]
                        positions2 = [int(pos) for pos in data2[j][3:].split(':')[1].split(',')]
                        pos1=0
                        pos2=0
                        dict1[doc] = []
                        while pos1 < len(positions1) and pos2 < len(positions2):
                            if positions1[pos1] < positions2[pos2]:
                                dict1[doc].append(positions1[pos1])
                                pos1 += 1
                            elif positions1[pos1] == positions2[pos2]:
                                dict1[doc].append(positions1[pos1])
                                pos1 += 1
                                pos2 += 1
                            else:
                                dict1[doc].append(positions2[pos2])
                                pos2 += 1
                        while pos1 < len(positions1):
                            dict1[doc].append(positions1[pos1])
                            pos1 += 1
                        while pos2 < len(positions2):
                            dict1[doc].append(positions2[pos2])
                            pos2 += 1
                        i += 1
                        j += 1
                    else:
                        doc = data2[j][3:].split(':')[0]
                        positions = [int(pos) for pos in data2[j][3:].split(':')[1].split(',')]
                        dict1[doc] = positions
                        j += 1
                else:
                    break
            while i < len(data1):
                if data1[i].startswith('   '):
                    doc = data1[i][3:].split(':')[0]
                    positions = [int(pos) for pos in data1[i][3:].split(':')[1].split(',')]
                    dict1[doc] = positions
                    i += 1
                else:
                    break
            while j < len(data2):
                if data2[j].startswith('   '):
                    doc = data2[j][3:].split(':')[0]
                    positions = [int(pos)for pos in data2[j][3:].split(':')[1].split(',')]
                    dict1[doc] = positions
                    j += 1
                else:
                    break
            merged.append(f'{word}:{len(dict1)}')
            for doc in dict1:
                positions = ' '
                for pos in dict1[doc]:
                    positions += f'{pos},'
                positions = positions[:-1]
                merged.append(f'   {doc}:{positions}')
        else:
            merged.append(data2[j])
            j += 1
            while j < len(data2):

                if data2[j].startswith('   '):
                    merged.append(data2[j])
                    j += 1
                else:
                    break
    if i < len(data1):
        merged.extend(data1[i:])
    if j < len(data2):
        merged.extend(data2[j:])
    with open(filepath, 'w') as file:
        for line in merged:
            file.write(line + '\n')
    file.close()

def output_from_dict(filepath, postings, doc_count):
    sorted_postings = dict(sorted(postings.items()))
    with open(filepath, 'w') as outFile:
        data1 = outFile.read().splitlines()
    i=0
    j=0
    merged = []
    while i <len(data1):
        if data1[i].split(':')[0] < sorted_postings[j]:
            merged.append(data1[i])
            i += 1
            while i < len(data1):
                if data1[i].startswith('   '):
                    merged.append(data1[i])
                    i += 1
                else:
                    break
        elif data1[i].split(':')[0] == sorted_postings[j]:
            word = data1[i].split(':')[0]
            i += 1
            dict1 = {}
            while i < len(data1) :
                if data1[i].startswith('   '):
                    doc = data1[i][3:].split(':')[0]
                    positions = [int(pos) for pos in data1[i][3:].split(':')[1].split(',')]
                    dict1[doc] = positions
                    i += 1
                else:
                    break
            for positions in sorted_postings[j]:
                doc = positions.split(':')[0]
                positions = [int(pos) for pos in positions.split(':')[1].split(',')]
                dict1[doc].append(positions)
            
            merged.append(f'{word}:{len(dict1)}')
            for doc in dict1:
                dict1[doc] = list(set(sorted(dict1[doc])))
                positions = ''
                for pos in dict1[doc]:

                    positions += f'{pos},'
                positions = positions[:-1]
                merged.append(f'   {doc}:{positions}')
            j += 1
        else:
            line1 = f'{sorted_postings[j]}:{doc_count[sorted_postings[j]]}\n'
            merged.append(line1)
            for positions in sorted_postings[j]:
                merged.append('   ' + positions)
            j += 1
            

                
    

    

        

            
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
    add_to_index(index, index_add)

    print(get_index('00000'))
    print(get_index('design'))
