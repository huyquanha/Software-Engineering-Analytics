import numpy
import prepare_data
import sys

args = prepare_data.arg_passing(sys.argv)
numpy.random.seed(args['-seed'])

from keras.optimizers import *
from keras.objectives import *
from create_model import *

from collections import namedtuple
import gzip
import cPickle

sys.path.append('/Users/Morakot/Dropbox/[github]/MSR2018/model-code/NCE')
sys.path.append('/Users/Morakot/Dropbox/[github]/MSR2018/model-code/')
sys.path.append('/Users/Morakot/Dropbox/[github]/MSR2018/model-code/classifier')
sys.path.append('../NCE')

# import load_data


################################# LOAD DATA #######################################################

print 'load parameters...'
try:
    feature = args['-feature']
    print feature
    dataset = args['-data']
    nnet_model = args['-nnetM']
    saving = args['-saving']
    if 'lstm' in feature:
        pretrain = args['-pretrain']
        dim = int(args['-dim'])
        maxlen= int(args['-len'])
        print dim
    if 'doc2vec' in feature:
        dim = str(args['-dim'])
        print dim
    regs = args['-reg']
    node_size = int(args['-node_size'])
except:
    feature = 'lstm'
    pretrain = 'kave_1'
    dataset = 'kave_1'
    nnet_model = 'dense'
    saving = 'test_lstm_distance_NN'
    dim = 10
    regs = ['inphid']
    node_size = 1

dataset_lstm = '/Users/Morakot/Dropbox/[github]/MSR2018/model-code/NCE/lstm2v_feature/lstm2v_kave_1_kave_1_dim10.pkl.gz'



if feature == 'lstm':
    print 'load lstm feature...'
    dataset_lstm = '../NCE/lstm2v_feature/lstm2v_' + dataset + '_' + pretrain + '_dim' + str(dim) + '_len' + str(maxlen) + '.pkl.gz'
    train_x, train_y, valid_x, valid_y, test_x, test_y = prepare_data.load_lstm2v_features(dataset_lstm)
else:
    print 'check a feature type input'

# set dropout
if 'hid' in regs:
    dropout_hid = True
    print 'Dropout layer: True'
else:
    dropout_hid = False

print '---training set---'
print train_x.shape
print train_y.shape

print '---valid set---'
print valid_x.shape
print valid_y.shape

print '---testset---'
print test_x.shape
print test_y.shape
print '-------------'

# n_classes = train_y.shape[-1]
# n_features = train_x.shape[-1]
# set loss
# loss = multi_label_loss

if train_y.dtype == 'float32':
    n_classes = -1
    loss = mean_squared_error
elif max(train_y) > 1:
    n_classes = max(train_y) + 1
    loss = sparse_categorical_crossentropy
else:
    n_classes = 1
    loss = binary_crossentropy

###################################### BUILD MODEL##################################################
print 'Building model...'

# n_classes, vocab_size, inp_len, emb_dim,
# seq_model='lstm', nnet_model='highway', pool_mode='mean',
# dropout_inp=False, dropout_hid=True

model = create_dense_multiclass(n_features=dim, n_classes=n_classes,
                                 hidden_node_size=int(dim / node_size), nnet_model=nnet_model,
                                 dropout=dropout_hid)

model.summary()
opt = RMSprop(lr=0.02)
model.compile(optimizer=opt, loss=loss)

fParams = 'bestmodels/' + saving + '.hdf5'
fResult = saving + '.txt'

if n_classes == -1:
    type = 'linear'
elif n_classes == 1:
    type = 'binary'
else:
    type = 'multi'

print type

saveResult = SaveResult([valid_x, valid_y, test_x, test_y],
                        metric_type=type, fileResult=fResult, fileParams=fParams)

callbacks = [saveResult, NanStopping()]
his = model.fit(train_x, train_y,
                validation_data=(valid_x, valid_y),
                nb_epoch=1000, batch_size=100, callbacks=callbacks)
