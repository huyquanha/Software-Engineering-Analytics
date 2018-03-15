import os
# os.environ['THEANO_FLAGS'] = 'device=cuda,floatX=float32'
# os.environ['CPLUS_INCLUDE_PATH'] = '/usr/local/cuda-8.0/include -lcudnn /usr/local/cuda-8.0/lib64'
# os.environ['LDFLAGS'] = '-L/usr/local/cuda-8.0/lib64 -lcudnn'
# export LDFLAGS='-L/usr/local/cuda-8.0/lib64 -lcudnn'


from keras.layers import *
from keras.models import Model
from keras.constraints import *
from keras.regularizers import *
import gzip
import numpy
import cPickle
import sys

import load_data
import noise_dist
from NCE import *



arg = load_data.arg_passing(sys.argv)
try:
    arg = load_data.arg_passing(sys.argv)
    dataset = '../dataset/data/' + arg['-data'] + '_pretrain.pkl.gz'
    saving = arg['-saving']
    emb_dim = int(arg['-dim'])
    max_len = int(arg['-len'])
    log = 'log/' + saving + '.txt'
    vocab_size = int(arg['-vocab'])
# ------------------------------------------------------------------
except:
    # arg = load_data.arg_passing(sys.argv)
    print 'set test parameters...'
    emb_dim = 10
    data_pretrain = 'lstm2v_' + 'kave_1' + '_dim' + str(emb_dim)
    dataset = '../dataset/data/' + 'kave_1' + '_pretrain.pkl.gz'    #/Users/Morakot/Dropbox/[github]/MSR2018/model-code/dataset/data/kave_1.pkl.gz
    saving = 'test'
    max_len = 100
    log = 'log/' + 'test' + '.txt'

    vocab_size = 9000
    # test environment
    sys.path.extend('/Users/ASUS/Documents/msr/model-code/NCE/')
    sys.path.extend('/Users/ASUS/Documents/msr/model-code/Classifier/')
    sys.path.extend('/Users/ASUS/Documents/msr/model-code/dataset/data/')
    # dataset_lstm = '/Users/Morakot/Dropbox/PythonWorkspace/PredictingComponent-multilabel/NCE/lstm2v_feature/lstm2v_CB_apache_dim50.pkl.gz'
    # dataset_distance = '/Users/Morakot/Dropbox/PythonWorkspace/PredictingComponent-multilabel/NCE/distance_feature/tfidf_cosine_CB.pkl.gz'
# ------------------------------------------------------------------
# emb_dim = '10'
# data_pretrain = 'lstm2v_' + 'kave_1' + '_dim' + str(emb_dim)
# dataset = data
# saving = 'test'
# max_len = '100'




n_noise = 100
print 'Loading data...'
train, valid, test = load_data.load(dataset) #load from the pretrain dataset
#valid = valid[-5000:]


print 'vocab: ', vocab_size

######################################################
# prepare_lm load data and prepare input, output and then call the prepare_mask function
# all word idx is added with 1, 0 is for masking -> vocabulary += 1
train_x, train_y, train_mask = load_data.prepare_lm(train, vocab_size, max_len)
valid_x, valid_y, valid_mask = load_data.prepare_lm(valid, vocab_size, max_len)

print 'Dataset size: Train: %d, valid: %d' % (len(train_x), len(valid_x))

vocab_size += 1
n_samples, inp_len = train_x.shape #get the tuple of dimensions from train_x => get back the n_samples (number of non-zero length seqs) and inp_len=maxlen (in load_data.py)

# Compute noise distribution and prepare labels for training data: next words from data + next words from noise
Pn = noise_dist.calc_dist(train, vocab_size)

labels = numpy.zeros((n_samples, inp_len, n_noise + 2), dtype='int64') #n_noise plus 2 is for train_mask (all 1) and array of 1s
labels[:, :, 0] = train_mask
labels[:, :, 1] = 1

print 'Building model...'
# Build model
main_inp = Input(shape=(inp_len,), dtype='int64', name='main_inp') #input length is maxlen (inp_len = maxlen), one dimension
next_inp = Input(shape=(inp_len,), dtype='int64', name='next_inp')

# Embed the context words to distributed vectors -> feed to GRU layer to compute the context vector
emb_vec = Embedding(output_dim=emb_dim, input_dim=vocab_size, input_length=inp_len,
                    #dropout=0.2,
                    mask_zero=True)(main_inp) #embedding Layer. main_inp is inputted to output emb_vec. emb_vec shape is (vocab_size,inp_len,emb_dim)

GRU_context = LSTM(input_dim=emb_dim, output_dim=emb_dim,
                   return_sequences=True)(emb_vec) #construct LSTM layer from emb_vec. Return the full sequence
#GRU_context = Dropout(0.5)(GRU_context)

# feed output of GRU layer to NCE layer
nce_out = NCE_seq(input_dim=emb_dim, input_len=inp_len, vocab_size=vocab_size, n_noise=n_noise, Pn=Pn,
              )([GRU_context, next_inp]) #the list of GRU_context and next_inp will be used in call() method as inputs
nce_out_test = NCETest_seq(input_dim=emb_dim, input_len=inp_len, vocab_size=vocab_size)([GRU_context, next_inp])

# Call a model
model = Model(input=[main_inp, next_inp], output=[nce_out])
print model.summary()

optimizer = RMSprop(lr=0.02, rho=0.99, epsilon=1e-7) #optimizer = RMSprop(lr=0.01)
model.compile(optimizer=optimizer, loss=NCE_seq_loss)

testModel = Model(input=[main_inp, next_inp], output=[nce_out_test])
testModel.compile(optimizer='rmsprop', loss=NCE_seq_loss_test)

# save result to the filepath and wait if the result doesn't improve after 3 epochs, the lr will be divided by 2
fParams = 'bestmodels/' + saving + '.hdf5'
callback = NCETestCallback(data=[valid_x, valid_y, valid_mask], testModel= testModel,
                           fResult=log, fParams=fParams)

json_string = model.to_json()
fModel = open('models/' + saving + '.json', 'w')
fModel.write(json_string)

print 'Training...'
his = model.fit([train_x, train_y], labels,
          batch_size=100, nb_epoch=20,
          callbacks=[callback])
