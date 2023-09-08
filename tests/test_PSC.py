import unittest

import sys,os
SCRIPT_DIR = os.path.dirname(os.path.abspath("ParametricSpectralClustering"))
sys.path.append(os.path.dirname(SCRIPT_DIR))

from ParametricSpectralClustering import PSC, Four_layer_FNN
from sklearn.cluster import KMeans
from sklearn.datasets import load_digits
import numpy as np
import torch
import random
import pickle

digits = load_digits()
x = digits.data/16
y = digits.target
torch.manual_seed(0)
np.random.seed(0)
random.seed(0)
clust_method = KMeans(n_clusters=10, init="k-means++", n_init=1, max_iter=100, algorithm='elkan')
model = Four_layer_FNN(64, 128, 256, 64, 10)
psc = PSC(model=model, clustering_method=clust_method, test_splitting_rate=0.3)
cluster_idx = psc.fit_predict(x)

class testPSC(unittest.TestCase):
    
    def test_init(self):

        self.assertIs(type(psc.n_neighbor), int)
        self.assertIs(type(psc.sigma), int)
        self.assertIs(type(psc.k), int)
        self.assertIs(type(psc.model), Four_layer_FNN)
        self.assertIs(type(psc.criterion), torch.nn.modules.loss.MSELoss)
        self.assertIs(type(psc.clustering), KMeans)
        self.assertIs(type(psc.test_splitting_rate), float)
        self.assertIs(type(psc.optimizer), torch.optim.Adam)
        self.assertIs(type(psc.epochs), int)
        self.assertIs(type(psc.model_fitted), bool)

        self.assertEqual(psc.n_neighbor, 8)
        self.assertEqual(psc.sigma, 1)
        self.assertEqual(psc.k, 10)
        self.assertEqual(psc.test_splitting_rate, 0.3)
        self.assertEqual(psc.epochs, 50)
        self.assertEqual(psc.clustering, clust_method)
    
    # output shape of fit_predict and predict
    def test_output_shape(self):
        self.assertEqual(x.shape, (1797, 64))
        output = psc.fit_predict(x)
        self.assertEqual(output.shape, (1797, ))
        output = psc.predict(x)
        self.assertEqual(output.shape, (1797, ))

    # train model
    def test_training_psc_model(self):
        U = psc.training_psc_model(x)
        self.assertIs(type(U), np.ndarray)
        self.assertEqual(U.shape, (1797, 10))

    def test_set_model(self):
        psc.set_model(model)
        self.assertEqual(psc.model, model)

    def test_save_model(self):
        psc.save_model("test_save_model")
        self.assertEqual(os.path.exists("test_save_model"), True)
        
        psc.fit(x)
        psc.save_model("test_save_fit_model")
        self.assertEqual(os.path.exists("test_save_fit_model"), True)

        m1 = None
        m2 = None
        with open("test_save_model", 'wb') as f1:
            pickle.dump(m1, f1)
        with open("test_save_fit_model", 'wb') as f2:
            pickle.dump(m2, f2)
        self.assertEqual(m1, m2)

    def test_load_model(self):
        psc.load_model("test_load_model")
        self.assertEqual(os.path.exists("test_load_model"), True)
        self.assertEqual(psc.model_fitted, True)


if __name__ == '__main__':
    unittest.main()
