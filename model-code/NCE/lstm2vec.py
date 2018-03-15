import sys

from keras.layers import *
from keras.models import Model
from keras.constraints import *
from keras.regularizers import *
from keras.models import model_from_json
import gzip
import numpy
import cPickle

import load_data
import noise_dist
from NCE import *

print 'load parameters...'

arg = load_data.arg_passing(sys.argv)
try:

    emb_dim = arg['-dim']
    max_len = int(arg['-len'])
    data_pretrain = 'lstm2v_' + arg['-dataPre'] + '_dim' + str(emb_dim) +'_len' + str(max_len)
    dataset = '../dataset/data/' + arg['-data'] + '.pkl.gz'
    saving = arg['-saving']

    model_path = 'models/' + data_pretrain + '.json'
    param_path = 'bestmodels/' + data_pretrain + '.hdf5'

    vocab_size = int(arg['-vocab'])
# ------------------------------------------------------------------
except:
    # arg = load_data.arg_passing(sys.argv)
    print 'set test parameters...'
    emb_dim = '10'
    data_pretrain = 'lstm2v_' + 'kave_1' + '_dim' + str(emb_dim)
    dataset = '../dataset/data/' + 'kave_1' + '.pkl.gz'    #/Users/Morakot/Dropbox/[github]/MSR2018/model-code/dataset/data/kave_1.pkl.gz
    saving = 'test'
    max_len = 100

    model_path = '/Users/Morakot/Dropbox/[github]/MSR2018/model-code/NCE/models/' + data_pretrain + '.json'
    param_path = 'bestmodels/' + data_pretrain + '.hdf5'

    vocab_size = 9000
    # test environment
    sys.path.extend('/Users/Morakot/Dropbox/[github]/MSR2018/model-code/NCE/')
    sys.path.extend('/Users/Morakot/Dropbox/[github]/MSR2018/model-code/Classifier/')
    sys.path.extend('/Users/Morakot/Dropbox/[github]/MSR2018/model-code/dataset/data/')
    # dataset_lstm = '/Users/Morakot/Dropbox/PythonWorkspace/PredictingComponent-multilabel/NCE/lstm2v_feature/lstm2v_CB_apache_dim50.pkl.gz'
    # dataset_distance = '/Users/Morakot/Dropbox/PythonWorkspace/PredictingComponent-multilabel/NCE/distance_feature/tfidf_cosine_CB.pkl.gz'
# ------------------------------------------------------------------
# emb_dim = '10'
# data_pretrain = 'lstm2v_' + 'kave_1' + '_dim' + str(emb_dim)
# dataset = data
# saving = 'test'
# max_len = '100'

print 'vocab: ', vocab_size

# save result to the filepath and wait if the result doesn't improve after 3 epochs, the lr will be divided by 2


custom = {'NCEContext': NCEContext, 'NCE': NCE, 'NCE_seq': NCE_seq}
fModel = open(model_path)
model = model_from_json(fModel.read(), custom_objects=custom)
model.load_weights(param_path)

# end pretraining.
# to distance_feature
train, train_labels, valid, valid_labels, test, test_labels = load_data.load_lstm2v(dataset)

# print len(valid)
# print len(valid_labels)

train_x, train_mask = load_data.prepare_lm_test(train, vocab_size, max_len)
valid_x, valid_mask = load_data.prepare_lm_test(valid, vocab_size, max_len)
test_x, test_mask = load_data.prepare_lm_test(test, vocab_size, max_len)
get_lstm_output = K.function([model.layers[0].input],
                             [model.layers[2].output])

print get_lstm_output

def lstm2feature(vecs, mask):
    # vecs: n_samples * n_steps * emb_dim
    # mask: n_samples * n_steps
    feats = vecs * mask[:, :, None]
    feats = numpy.sum(feats, axis=1) / numpy.sum(mask, axis=1)[:, None]
    return feats

# print len(train_x)

train_lstm = get_lstm_output([train_x])[0]
valid_lstm = get_lstm_output([valid_x])[0]
test_lstm = get_lstm_output([test_x])[0]

train_feats = lstm2feature(train_lstm, train_mask)
valid_feats = lstm2feature(valid_lstm, valid_mask)
test_feats = lstm2feature(test_lstm, test_mask)

f = gzip.open('lstm2v_feature/' + saving + '.pkl.gz', 'wb')
cPickle.dump((train_feats, train_labels, valid_feats, valid_labels, test_feats, test_labels), f)
f.close()