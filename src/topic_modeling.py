"""
Make use of Gensim to try out HDP topic modeling.
"""


from gensim import corpora, models, similarities, matutils
from src.data_processing.matrix_generation import *
import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)


def hdp_model():
    """
    Formats cocktail data and builds an HDP model.
    :return: Gensim HDP model
    """
    dataframe = recipe_data(Normalization.ROW_SUM_ONE, 2)
    corpus = matutils.Dense2Corpus(dataframe.values.transpose())
    id2word = {}
    for i in range(len(dataframe.columns)):
        id2word[i] = dataframe.columns[i]
    return models.HdpModel(corpus, id2word, max_chunks=None, max_time=None,
                           chunksize=10, kappa=1.0, tau=64.0, K=10, T=30,
                           alpha=1, gamma=1, eta=0.01, scale=1.0,
                           var_converge=0.0001)


if __name__ == '__main__':
    hdp = hdp_model()
    #hdp.print_topics()
    print "DONE"
    hdp.optimal_ordering()
    hdp.print_topics(topics=-1)