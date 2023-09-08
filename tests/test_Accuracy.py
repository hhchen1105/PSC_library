import unittest

import sys,os
SCRIPT_DIR = os.path.dirname(os.path.abspath("ParametricSpectralClustering"))
sys.path.append(os.path.dirname(SCRIPT_DIR))

from ParametricSpectralClustering import PSC, Accuracy
from sklearn.datasets import load_digits
import numpy as np
from unittest.mock import patch
import io

digits = load_digits()
x = digits.data/16
y = digits.target
psc = PSC()
cluster_idx = psc.fit_predict(x)
acc = Accuracy(y_true=y, y_pred=cluster_idx)

class testAccuracy(unittest.TestCase):
    def test_cluster_acc(self):
        self.assertIs(type(acc.cluster_acc()), np.float64)
            
    def test_ARI(self):
        self.assertIs(type(acc.ARI()), float)

    def test_AMI(self):
        self.assertIs(type(acc.AMI()), np.float64)

    def test_acc_report(self):
        with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
            acc.acc_report()
            printed_output = mock_stdout.getvalue()
        self.assertTrue(printed_output.strip(), msg="Function didn't print anything")

if __name__ == "__main__":
    unittest.main()
