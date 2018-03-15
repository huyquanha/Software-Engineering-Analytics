import os

# This run_script runs classifiers. select mode to run

# mode option
#   lstm-highway:
#       this is end-to-end approach using trained embedding matrix to initiated LSTM and uses Highway as a classifier.
#       output: The result is in /classification/log
#               <project name>_lstm_highway_dim<number of dimensions>_reginphid_prefixed_lm_poolmean.txt
#               Model is in models/HBASE_lstm_highway_dim10_reginphid_prefixed_lm_poolmean.json
#
#   lstm-NeuralNet:
#       this is end-to-end approach using trained embedding matrix to initiated LSTM and uses tradition Neural Net. as a classifier.
#       output: The result is in /classification/log
#               <project name>_lstm_NN_dim<number of dimensions>_reginphid_prefixed_lm_poolmean.txt
#               Model is in models/HBASE_lstm_highway_dim10_reginphid_prefixed_lm_poolmean.json
#
#   lstm-rf:
#       this mode runs RF using the distance_feature vectors extracted from trained LSTM
#       output: The result is in /classification/log
#               RF_lstm2v_<project name>_dim<number of dimensions>.txt
#
#   BoW-NeuralNet:
#       this is baseline for document representation using BoW and neural network
#       output: The result is in /classification/log
#               <project name>_bow_NN.txt
#               HBASE_bow_NN.txt
#   frequency:
#       this is a baseline using freguency of the components


# modeList = ['lstm-NeuralNet-e2e']
modeList = ['lstm-NeuralNet']



dataNames = ['kave_1', 'kave_2', 'kave_3', 'kave_4', 'kave_5', 'kave_6', 'kave_7']
dataNames = ['kave_1']

dims = ['10', '50', '100', '200']

maxlens = ['120','200','500','1000']

# flag = 'THEANO_FLAGS=''mode=FAST_RUN,device=gpu,floatX=float32'' '
flag = ''
regs = ['hid','no']
note = ''  # nospace

for mode in modeList:
    if mode == 'lstm-NeuralNet':
        # note = '5_lr=0.03,ep=300,bs=100,nodropout'
        feature = 'lstm'
        node_sizes = ['1']
        nnet_model = 'dense'
        for reg in regs:
            for maxlen in maxlens:
                for dataName in dataNames:
                    for dim in dims:
                        for node_size in node_sizes:
                            cmd = flag + 'python training.py -data ' + dataName + ' -pretrain ' + dataName + \
                                  ' -feature ' + feature + ' -nnetM ' + nnet_model + ' -dim ' + dim + ' -len ' + maxlen + \
                                  ' -reg ' + reg + ' -node_size ' + node_size

                            cmd += ' -saving ' + dataName + '-pretrain_' + dataName + '_lstm_' + \
                                   nnet_model + '_dim_' + dim + '_len' + maxlen + \
                                   '_reg' + reg + '_node_size_' + node_size

                            print cmd
                            os.system(cmd)