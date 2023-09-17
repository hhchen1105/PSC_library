import unittest
from ParametricSpectralClustering import PSC, Four_layer_FNN
from sklearn.cluster import KMeans
from sklearn.datasets import load_digits

digits = load_digits()
x = digits.data/16
model = Four_layer_FNN(64, 128, 256, 64, 10)
clustering_method = KMeans(n_clusters=10, init="k-means++", n_init=1, max_iter=100, algorithm='elkan')

class NullClusteringMethod():
    def __init__(self, x) -> None:
        self.nullString = ""
        self.x = x
    def someRandomFunction(self):
        self.nullString = "some random function"
null_clustering_method = NullClusteringMethod(x)

class ErrorHandling(unittest.TestCase):

    def test_raise_fit_AttributeError(self):
        psc = PSC(model=model, clustering_method=null_clustering_method)
        with self.assertRaises(AttributeError):
            psc.fit(x)

    def test_raise_fit_predict_AttributeError(self):
        psc = PSC(model=model, clustering_method=null_clustering_method)
        with self.assertRaises(AttributeError):
            psc.fit_predict(x)

    def test_raise_predict_AttributeError(self):
        psc = PSC(model=model, clustering_method=null_clustering_method)
        with self.assertRaises(AttributeError):
            psc.predict(x)

    def test_raise_load_model_FileNotFoundError(self):
        psc = PSC(model=model, clustering_method=clustering_method)
        with self.assertRaises(FileNotFoundError):
            psc.load_model("omg")
    
    def test_raise_model_not_assigned_error(self):
        psc = PSC(clustering_method=clustering_method)
        psc.set_model(None)
        with self.assertRaises(ValueError):
            psc.fit(x)

    def test_raise_clustering_method_not_assigned_error(self):
        psc = PSC(model=model, clustering_method=None)
        with self.assertRaises(ValueError):
            psc.fit(x)

if __name__ == "__main__":
    unittest.main()
