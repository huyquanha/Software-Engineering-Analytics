import cPickle
import numpy
import theano

import gzip
import scipy.io as sio

def shared_data(data_xy, borrow=True):
    import theano.tensor as tensor
    data_x, data_y = data_xy

    shared_x = theano.shared(numpy.asarray(data_x,
                                           dtype=theano.config.floatX),
                             borrow=borrow)
    shared_y = theano.shared(numpy.asarray(data_y,
                                           dtype=theano.config.floatX),
                             borrow=borrow)
    return shared_x, tensor.cast(shared_y, 'int32')

def load(path):
    f = gzip.open(path, 'rb')
    train, valid, test = cPickle.load(f)
    print path, len(train[0]), len(valid[0])

    return train, valid, test

def load_all(path):
    f = gzip.open(path, 'rb')

    train_t, train_d, train_y, \
    valid_t, valid_d, valid_y, \
    test_t, test_d, test_y = cPickle.load(f)

    return train_t, train_d, train_y, valid_t, valid_d, valid_y, test_t, test_d, test_y

def load_data(path):
    f = gzip.open(path, 'rb')
    train_t, train_d, train_labels, valid_t, valid_d, valid_labels, test_t, test_d, test_labels = cPickle.load(f)

    train = train_t + train_d
    valid = valid_t + valid_d
    test = test_t + test_d

    return train, valid, test

def load_lstm2v(path):
    f = gzip.open(path, 'rb')
    train_t, train_d, train_labels, valid_t, valid_d, valid_labels, test_t, test_d, test_labels = cPickle.load(f)

    train = train_t #+ train_d
    valid = valid_t #+ valid_d
    test = test_t #+ test_d

    return train, train_labels, valid, valid_labels, test, test_labels

def prepare_NCE(seqs, n_context=2, vocab_size=10000, max_len=3000):
    new_seqs = []
    for i, s in enumerate(seqs):
        new_s = [w if w < vocab_size else 0 for w in s]
        new_seqs.append(new_s)
    seqs = new_seqs

    n_samples = 0
    for s in seqs: n_samples += max(0, min(max_len + 1, len(s)) - n_context)

    x = numpy.zeros((n_samples, n_context)).astype('int64')
    y = numpy.zeros((n_samples, 1)).astype('int64')

    idx = 0
    for s in seqs:
        for i in range(min(max_len + 1, len(s)) - n_context):
            x[idx] = s[i : i + n_context]
            y[idx] = s[i + n_context]

            idx += 1

    return x, y

def prepare_lm_test(seqs, vocab_size=10000, max_len=100):
    new_seqs = []
    for i, s in enumerate(seqs):
        new_s = [w if w < vocab_size else 0 for w in s]
        if len(new_s) < 1: new_s = [0]
        new_seqs.append(new_s)
    seqs = new_seqs

    lengths = [min(max_len, len(s)) for s in seqs]
    maxlen = max(lengths)
    print lengths
    n_samples = len(seqs)

    x = numpy.zeros((n_samples, max_len)).astype('int64')
    mask = numpy.zeros((n_samples, max_len)).astype('int64')

    for i, s in enumerate(seqs):
        # print len(s)
        l = lengths[i]
        mask[i, :l] = 1
        x[i, :l] = s[:l]
        x[i] += mask[i]

    return x, mask

def prepare_lm(seqs, vocab_size=10000, max_len=100):
    new_seqs = []
    for i, s in enumerate(seqs):
        new_s = [w if w < vocab_size else 0 for w in s] #only take w(the order of the count of correspond word) if it < vocab_size => only takes the most popular ones
        new_seqs.append(new_s)
    seqs = new_seqs

    lengths = [min(max_len, len(s)-1) for s in seqs]
    maxlen = max(lengths)
    n_samples = numpy.count_nonzero(lengths) #count the number of non-zero values in lengths array

    x = numpy.zeros((n_samples, maxlen)).astype('int64') #create n_samples arrays of 0s, each of length maxlen. Type is int64
    y = numpy.zeros((n_samples, maxlen)).astype('int64')
    mask = numpy.zeros((n_samples, maxlen)).astype('int64')

    idx = 0 #each idx is a sample
    for i, s in enumerate(seqs): #for each sequence
        l = lengths[i]
        if l < 1: continue
        mask[idx, :l] = 1
        x[idx, :l] = s[:l] #initialize each item in sample (from 0 to l-1) to s[correspond index]
        y[idx, :l] = s[1 : l+1] #initialize from s[1] to s[l+1]
        x[idx] += mask[idx] #add 1 to each item in x[idx]
        y[idx] += mask[idx] #add 1 to each item in y[idx]
        idx += 1

    return x, y, mask

def arg_passing(argv):
    i = 1
    arg_dict = {}
    while i < len(argv) - 1:
        arg_dict[argv[i]] = argv[i+1]
        i += 2
    return arg_dict


