import os
from datetime import datetime

modeList = ['pretrain-lstm']
# modeList = ['lstm2vec']
# modeList = ['cosine_feature']
# modeList = ['doc2vec']

dataNames = ['kave_1', 'kave_2', 'kave_3', 'kave_4', 'kave_5', 'kave_6', 'kave_7']
dataNames = ['kave_1']

dims = ['10', '50', '100', '200']
#dims=['100','200']

vocab = '9000'

maxlens = ['120','200','500','1000']
#maxlens=['200','500','1000']

# flag = 'THEANO_FLAGS=''mode=FAST_RUN,device=gpu,floatX=float32'' '
flag = ''

start_time_all = datetime.now()
for mode in modeList:
    if mode == 'pretrain-lstm':
        for dim in dims:
            for maxlen in maxlens:
                for dataName in dataNames:
                    start_time = datetime.now()
                    print 'Start at: {}'.format(start_time)
                    command = flag + 'python lstm_pretrain.py -data ' + dataName + ' -saving lstm2v_' + dataName + '_dim' + dim + '_len' + maxlen + ' -vocab ' + vocab + ' -dim ' + dim + ' -len ' + maxlen
                    print command
                    os.system(command)

                # command = 'python lstm2vec.py -dataPre ' + dataName + ' -data ' + dataName + ' -vocab ' + vocab + ' -dim ' + dim + ' -len ' + maxlen + ' -saving lstm2v_' + dataName + '_' + dataName + '_dim' + dim
                # print command
                # os.system(command)
                # # end_time = datetime.now()
            #
            # print 'Start at:\t{}'.format(start_time)
            # print 'End at:\t{}'.format(end_time)
            # print('Duration:\t{}'.format(end_time - start_time))

    # elif mode == 'lstm2vec':
    #     for project, repo in dataset.items():
    #         for dim in dims:
    #             command = 'python lstm2vec.py -dataPre ' + repo + ' -data ' + project + ' -vocab ' + vocab + ' -dim ' + dim + ' -len ' + maxlen + ' -saving lstm2v_' + project + '_' + repo + '_dim' + dim
    #             print command
    #             os.system(command)
    #
    # elif mode == 'cosine_feature':
    #     for project, repo in dataset.items():
    #         command = 'python cosine.py -data ' + project + ' -saving tfidf_cosine_' + project
    #         print command
    #         os.system(command)
    # elif mode == 'doc2vec':
    #     dims = ['10', '50', '100', '200']
    #     for project, repo in dataset.items():
    #         for dim in dims:
    #             command = 'python doc2vec.py -data ' + project + ' -dim ' + dim + ' -saving doc2vec_' + project + '_dim' + dim
    #             print command
    #             os.system(command)

end_time_all = datetime.now()
print '##############################'
print 'Start at:\t{}'.format(start_time_all)
print 'End at:\t{}'.format(end_time_all)
print 'Duration all:\t{}'.format(end_time_all - start_time_all)
