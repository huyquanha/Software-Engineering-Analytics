import cPickle
import sys
import gzip
import numpy
from subprocess import Popen, PIPE

'''parameter'''

dataFile = 'data/Data.pkl.gz'
trainingSize = 60
validationSize = 20
testSize = 20

chosen_frequency = 10


# ---------------------------------

def listtostring(word_id):
    str_id = []
    for i in range(len(word_id)):
        str_id.append(' '.join(map(str, word_id[i])))
    return str_id


def init_list_of_objects(size):
    list_of_objects = list()
    for i in range(0, size):
        list_of_objects.append(list())  # different object reference each time
    return list_of_objects


'''read data from Kevin, seperate sequence and testOutcome'''
data = gzip.open(dataFile, 'rb')
event = cPickle.load(data)

maxLen=0
totLen=0
for i in range(len(event[1])): #calculate maxlen and avglen of a sequence
    if len(event[1][i])>maxLen:
        maxLen=len(event[1][i])
    totLen+=len(event[1][i])

file = open('data/sequenceLength.txt', 'w')
file.write(str(maxLen)+" "+str(totLen/len(event[1])))


count_file = 1
for i in range(0, 5000, 5000):
    dataName = 'kave_' + str(count_file)
    '''testOutcome = numpy.array((event[2])[i:i + 5000])
    sequence = (event[1])[i:i + 5000]'''

    results = {0: [], 1: [], 2: [], 3: [], 4: []}
    sequence = []
    pre_train_sequence=[]
    testOutcome = []
    for j in range(len(event[2])):
        if len(results[event[2][j]]) < 10000:
            results[event[2][j]].append(j)

    for k in range(10000):
        for key in results:
            if k<len(results[key]) and k<5000:
                testOutcome.append(event[2][results[key][k]])
                sequence.append(event[1][results[key][k]])
                pre_train_sequence.append(event[1][results[key][k]])
            elif k<len(results[key]):
                pre_train_sequence.append(event[1][results[key][k]])

    '''convert sequence into long string'''
    sequence = numpy.array(listtostring(numpy.array(sequence)))
    pre_train_sequence=numpy.array(listtostring(numpy.array(pre_train_sequence)))
    testOutcome=numpy.array(testOutcome)

    '''divide date'''
    print 'No. of sequences: ' + str(len(testOutcome))

    if trainingSize + validationSize + testSize == 100:
        numData = len(testOutcome)
        numTrain = (trainingSize * numData) / 100
        numValidation = (validationSize * numData) / 100
        numTest = (testSize * numData) / 100

        print "Total data: %s" % numData
        print "Training size: %s, validation size: %s, testing size: %s" % (numTrain, numValidation, numTest)
        print "Total: %s" % (numTrain + numValidation + numTest)

        divided_set = numpy.zeros((len(testOutcome), 3)).astype('int64')

        divided_set[0:numTrain, 0] = 1
        divided_set[numTrain:numTrain + numValidation, 1] = 1
        divided_set[numTrain + numValidation :numData, 2] = 1

        f = open('data/' + dataName + '_3sets.txt', 'w')
        f.write('train\tvalid\ttest')
        for s in divided_set:
            f.write('\n%d\t%d\t%d' % (s[0], s[1], s[2]))
        f.close()
    else:
        print 'check size'

    '''pre-processing for pretrain'''


    def normalize(seqs):
        for i, s in enumerate(seqs):
            words = s.split()
            if len(words) < 1:
                seqs[i] = 'null'
        return seqs


    def load_pretrain(data):
        print len(data)
        print data
        data = numpy.array(data)
        return normalize(data.astype('str'))


    # tokenizer.perl is from Moses: https://github.com/moses-smt/mosesdecoder/tree/master/scripts/tokenizer
    tokenizer_cmd = ['/usr/bin/perl', 'tokenizer.perl', '-l', 'en', '-q', '-']
    #tokenizer_cmd = ['C:\\Users\\ASUS\\Documents\\msr\\model-code\\dataset', 'tokenizer.perl', '-l', 'en', '-q', '-']


    # tokenizer_cmd = ['/Users/Morakot/Dropbox/[github]/MSR2018/model-code/dataset', 'tokenizer.perl', '-l', 'en', '-q', '-']

    def tokenize(sentences): #use the power of regular expression to tokenize sentences
        print 'Tokenizing..',
        text = "\n".join(sentences)
        tokenizer = Popen(tokenizer_cmd, stdin=PIPE, stdout=PIPE)
        tok_text, _ = tokenizer.communicate(text)
        toks = tok_text.split('\n')[:-1]
        print 'Done'

        return toks


    def build_dict(sentences): #sentences is normalized pretrain_sequence
        sentences = tokenize(sentences)

        print 'Building dictionary..'
        wordcount = dict()
        for ss in sentences: #for each sequence in pretrain_sequence
            words = ss.strip().lower().split()
            for w in words: #for each word in that sequence
                if w not in wordcount:
                    wordcount[w] = 1
                else:
                    wordcount[w] += 1

        counts = wordcount.values()
        keys = wordcount.keys()

        # [start:stop:step]. Here step is -1 => sort the indices of counts in descending order of counts
        # counts=[5,7,3,2,4] => sorted_idx=[1,0,4,2,3]
        sorted_idx = numpy.argsort(counts)[::-1]
        counts = numpy.array(counts)

        print 'number of words in dictionary:', len(keys)

        worddict = dict()

        # worddict[keys[1]]= 0+1=1
        #worddict[keys[0]]=1+1=2
        #worddict[keys[4]]=2+1=3
        # => same keys as wordcount, the value is the order of count of that key with 1 being the highest, then 2, 3, ...
        for idx, ss in enumerate(sorted_idx):
            worddict[keys[ss]] = idx + 1  # leave 0 (UNK)

        #because sorted_ix is descendingly sorted, once counts[c] < chosen_frequency, pos is the number of words with larger frequency.
        pos = 0
        for i, c in enumerate(sorted_idx):
            if counts[c] >= chosen_frequency:
                pos = i

        print numpy.sum(counts), ' total words, ', pos, 'words with frequency >=', chosen_frequency

        print worddict
        return worddict

    #title is train=pretrain_sequence[train_ids]
    #description is valid = pretrain_sequence[valid_ids]
    #iterate over train and valid and add only the order of counts of the words that appear in the dictionary to the seqs
    def grab_data(title, description, dictionary):
        title = tokenize(title)
        description = tokenize(description)

        #seqs = [[None, None, None,...],[None, None, None,...]]
        seqs = [[None] * len(title), [None] * len(description)]
        for i, sentences in enumerate([title, description]): #i=0 is title, i=1 is description
            for idx, ss in enumerate(sentences): #for each sequence in title and description respectively
                words = ss.strip().lower().split() #get an array of words from each sequence
                #seqs[i][idx] is a list
                seqs[i][idx] = [dictionary[w] if w in dictionary else 0 for w in words] #put the values from dict in seqs if w is in dict (order of counts)
                if len(seqs[i][idx]) == 0: #if the sequence have no word in dictionary
                    print 'len 0: ', i, idx
                    print w

        #return pretrain, prevalid
        return seqs[0], seqs[1]


    pretrain_sequence = numpy.array(load_pretrain(pre_train_sequence))
    print 'number of datapoints:', len(pretrain_sequence)
    print "after building dict..."

    n_train = len(pretrain_sequence) * 2 // 3 #divide with integer result (discard remainder)
    ids = numpy.arange(len(pretrain_sequence))

    numpy.random.shuffle(ids)
    train_ids = ids[:n_train]
    valid_ids = ids[n_train:]

    train = pretrain_sequence[train_ids]
    valid = pretrain_sequence[valid_ids]

    print '--all--'
    #create a dictionary of keys as words and values as the order of the counts of each word (1 highest,2,3,...) in the pretrain_sequence
    dictionary = build_dict(pretrain_sequence)

    print '--train/valid--'
    pre_train, pre_valid = grab_data(train, valid, dictionary)

    f_pre = gzip.open('data/' + dataName + '_pretrain.pkl.gz', 'wb')
    cPickle.dump((pre_train, pre_valid, pre_valid), f_pre, -1)
    f_pre.close()

    f = gzip.open('data/' + dataName + '.dict.pkl.gz', 'wb')
    cPickle.dump(dictionary, f, -1)
    f.close()

    '''Prepare labeled data file'''

    f = open('data/' + dataName + '_3sets.txt', 'r')
    train_ids, valid_ids, test_ids = [], [], []

    count = -2
    for line in f:
        if count == -2:
            count += 1
            continue

        count += 1
        ls = line.split()
        if ls[0] == '1':
            train_ids.append(count)
        if ls[1] == '1':
            valid_ids.append(count)
        if ls[2] == '1':
            test_ids.append(count)
    f.close()
    print 'ntrain, nvalid, ntest: ', len(train_ids), len(valid_ids), len(test_ids)

    #these data will be used for actual training and classifier
    train_sequence, train_labels = sequence[train_ids], testOutcome[train_ids]
    valid_sequence, valid_labels = sequence[valid_ids], testOutcome[valid_ids]
    test_sequence, test_labels = sequence[test_ids], testOutcome[test_ids]


    print str(len(train_sequence)) + ' ' + str(len(train_labels))
    print str(len(valid_sequence)) + ' ' + str(len(valid_labels))
    print str(len(test_sequence)) + ' ' + str(len(test_labels))
    print '---'

    f_dict = gzip.open('data/' + dataName + '.dict.pkl.gz', 'rb')
    dictionary = cPickle.load(f_dict)
    train_t, train_d = grab_data(train_sequence, train_sequence, dictionary)
    valid_t, valid_d = grab_data(valid_sequence, valid_sequence, dictionary)
    test_t, test_d = grab_data(test_sequence, test_sequence, dictionary)
    f.close()

    f = gzip.open('data/' + dataName + '.pkl.gz', 'wb')

    # print train_labels.dtype
    train_labels = train_labels.astype(int)
    valid_labels = valid_labels.astype(int)
    test_labels = test_labels.astype(int)
    # print train_labels.dtype
    # print type(train_d)

    print str(len(train_t)) + ' ' + str(len(train_d)) + ' ' + str(len(train_labels))
    print str(len(valid_t)) + ' ' + str(len(valid_d)) + ' ' + str(len(valid_labels))
    print str(len(test_t)) + ' ' + str(len(test_d)) + ' ' + str(len(test_labels))

    print 'packing...'
    cPickle.dump((train_t, train_d, train_labels,
                  valid_t, valid_d, valid_labels,
                  test_t, test_d, test_labels), f, -1)
    f.close()

    count_file = count_file + 1
