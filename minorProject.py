from __future__ import print_function
import os

#for root,dirs,files in os.walk("/home/sarthakmeh/Desktop/Project"):
    for file in files:
        #Get all the files in root directory ending with .py.
        if file.endswith(".py"):
            f = os.path.join(root,file)
            list = open(f,"r")
            lines = list.readlines()
            # print each line in the file except the \n character
            for line in lines: 
                print(line[:-2]) 
                #match keyword and return the position in file
                #word = match_keyword(line)  
                #locate(word)
 
KEYWORD = 'BUG'

def match_keyword(tokens):
    length = len(tokens)
    for word in tokens : 
        if word == KEYWORD:
           return word     

def _evaluate(tokens):
    tag = test(tokens)
    if tag:
        return (tokens, tag)
    elif len(tokens) == 1:
        return (tokens, 'O')

def _splits(tokens):
    return ((tokens[:i], tokens[i:]) for i in xrange(min(len(tokens), MAX_PATTERN_LENGTH), 0, -1))

def sequential_pattern_match(tokens):
    return ifilter(bool, imap(_halves_match, _splits(tokens))).next()

def _halves_match(halves):
    result = _evaluate(halves[0])
    if result:
        return [result] + (halves[1] and sequential_pattern_match(halves[1]))

if __name__ == "__main__":
    tokens = "I went to a clinic to do a Barium Swallow Test because I had pain in stomach after taking Nexium".split()
    output = sequential_pattern_match(tokens)
    slashTags = ' '.join(t + '/' + tag for tokens, tag in output for t in tokens)
    print(slashTags)
    assert slashTags == "I/O went/O to/O a/O clinic/O to/O do/O a/O Barium/INTERVENTION Swallow/INTERVENTION Test/O because/O I/O had/O pain/SYMPTOM in/SYMPTOM stomach/SYMPTOM after/O taking/O Nexium/MEDICINE"

    import timeit
    t = timeit.Timer(
        'sequential_pattern_match("I went to a clinic to do a Barium Swallow Test because I had pain in stomach after taking Nexium".split())',
        'from __main__ import sequential_pattern_match'
    )
    print(t.repeat(3, 10000))
       

"""Define words as 2+ letters"""
def count_unique(s):
    count = 0
    if word in line:
        if len(word) >= 2:
            count += 1
    return count


"""Open text document, read it, strip it, then filter it"""
txt_file = open('charactermask.txt', 'r')

for line in txt_file:
    for word in line.strip().split():
        word = word.strip(punctuation).lower()
        if words_only.match(word):
               counter[word] += 1


# Most Frequent Words
top_words = sorted(counter.iteritems(),
                    key=lambda(word, count): (-count, word))[:number] 

print ('Most Frequent Words: ')

for word, frequency in top_words:
    print ("%s: %d") % (word, frequency)


# Least Frequent Words:
least_words = sorted(counter.iteritems(),
                    key=lambda (word, count): (count, word))[:number]

print ("Least Frequent Words: ")

for word, frequency in least_words:
    print ("%s: %d") % (word, frequency)


# Total Unique Words:
print ("Total Number of Unique Words: %s ") % total_unique
   
