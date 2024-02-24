import time
import warnings
import torch
import numpy as np
import matplotlib.pyplot as plt
import torch.nn as nn
import random
from sklearn import cluster, datasets, mixture
from sklearn.neighbors import kneighbors_graph
from sklearn.preprocessing import StandardScaler
from itertools import cycle, islice

from ParametricSpectralClustering.psc import PSC

r = 72
rng = np.random.RandomState(r)
torch.manual_seed(0)
random.seed(int(r))
np.random.seed(0)

# ============
# Generate datasets. We choose the size big enough to see the scalability
# of the algorithms, but not too big to avoid too long running times
# ============
n_samples = 10000
noisy_circles = datasets.make_circles(
    n_samples=n_samples, factor=0.5, noise=0.05, random_state=rng
)
x, y = noisy_circles
print(x.shape)
noisy_moons = datasets.make_moons(n_samples=n_samples, noise=0.05, random_state=rng)
blobs = datasets.make_blobs(n_samples=n_samples, random_state=8)
no_structure = np.random.rand(n_samples, 2), None

# Anisotropicly distributed data
random_state = 170
X, y = datasets.make_blobs(n_samples=n_samples, random_state=random_state)
transformation = [[0.6, -0.6], [-0.4, 0.8]]
X_aniso = np.dot(X, transformation)
aniso = (X_aniso, y)

# blobs with varied variances
varied = datasets.make_blobs(
    n_samples=n_samples, cluster_std=[1.0, 2.5, 0.5], random_state=random_state
)

# ============
# Set up cluster parameters
# ============
plt.figure(figsize=(7.5, 7.5))
plt.subplots_adjust(
    left=0.02, right=0.98, bottom=0.001, top=0.96, wspace=0.05, hspace=0.01
)

plot_num = 1

default_base = {
    "quantile": 0.3,
    "eps": 0.3,
    "damping": 0.9,
    "preference": -200,
    "n_neighbors": 10,
    "n_clusters": 3,
    "min_samples": 20,
    "xi": 0.05,
    "min_cluster_size": 0.1,
}

datasets = [
    (
        "noisy_circles",
        noisy_circles,
        {
            "damping": 0.77,
            "preference": -240,
            "quantile": 0.2,
            "n_clusters": 2,
            "min_samples": 20,
            "xi": 0.25,
        },
    ),
    (
        "noisy_moons",
        noisy_moons,
        {"damping": 0.75, "preference": -220, "n_clusters": 2},
    ),
    (
        "varied",
        varied,
        {
            "eps": 0.18,
            "n_neighbors": 2,
            "min_samples": 5,
            "xi": 0.035,
            "min_cluster_size": 0.2,
        },
    ),
    (
        "aniso",
        aniso,
        {
            "eps": 0.15,
            "n_neighbors": 2,
            "min_samples": 20,
            "xi": 0.1,
            "min_cluster_size": 0.2,
        },
    ),
    ("blobs", blobs, {}),
    ("no_structure", no_structure, {}),
]


# for noisy_circles, noisy_moons, blobs, no_structure
class Net1(nn.Module):
    def __init__(self, out_put):
        super(Net1, self).__init__()
        # Define the layers
        self.fc1 = nn.Linear(2, 32)
        self.fc2 = nn.Linear(32, 64)
        self.fc3 = nn.Linear(64, 128)
        self.fc4 = nn.Linear(128, 64)
        self.fc5 = nn.Linear(64, 32)
        self.output_layer = nn.Linear(32, out_put)

        self.relu = nn.ReLU()

    def forward(self, x):
        x = self.fc1(x)
        x = self.fc2(x)
        x = self.relu(x)
        x = self.fc3(x)
        x = self.fc4(x)
        x = self.relu(x)
        x = self.fc5(x)
        x = self.output_layer(x)
        return x


# for varied
class Net2(nn.Module):
    def __init__(self, out_put):
        super(Net2, self).__init__()
        # Define the layers
        self.fc1 = nn.Linear(2, 16)
        self.fc2 = nn.Linear(16, 32)
        self.fc3 = nn.Linear(32, 16)
        self.fc4 = nn.Linear(16, 8)
        self.output_layer = nn.Linear(8, out_put)
        self.relu = nn.ReLU()

    def forward(self, x):
        x = self.fc1(x)
        x = self.fc2(x)
        x = self.fc3(x)
        x = self.fc4(x)
        x = self.output_layer(x)
        return x


# for aniso
class Net3(nn.Module):
    def __init__(self, out_put):
        super(Net3, self).__init__()
        # Define the layers
        self.fc1 = nn.Linear(2, 32)
        self.fc2 = nn.Linear(32, 64)
        self.fc3 = nn.Linear(64, 32)
        self.fc4 = nn.Linear(32, 16)
        self.output_layer = nn.Linear(16, out_put)
        self.relu = nn.ReLU()

    def forward(self, x):
        x = self.fc1(x)
        x = self.fc2(x)
        x = self.fc3(x)
        x = self.fc4(x)
        x = self.output_layer(x)
        return x


for i_dataset, (name, dataset, algo_params) in enumerate(datasets):
    # update parameters with dataset-specific values
    params = default_base.copy()
    params.update(algo_params)

    X, y = dataset

    # normalize dataset for easier parameter selection
    X = StandardScaler().fit_transform(X)

    # estimate bandwidth for mean shift
    bandwidth = cluster.estimate_bandwidth(X, quantile=params["quantile"])

    # connectivity matrix for structured Ward
    connectivity = kneighbors_graph(
        X, n_neighbors=params["n_neighbors"], include_self=False
    )
    # make connectivity symmetric
    connectivity = 0.5 * (connectivity + connectivity.T)

    # ============
    # Create cluster objects
    # ============
    KMeans = cluster.KMeans(
        n_clusters=params["n_clusters"],
        init="random",
        n_init="auto",
        algorithm="elkan",
        random_state=rng,
    )
    spectral = cluster.SpectralClustering(
        n_clusters=params["n_clusters"],
        eigen_solver="arpack",
        affinity="nearest_neighbors",
        random_state=rng,
    )
    torch.manual_seed(0)
    model_1 = Net1(params["n_clusters"])
    torch.manual_seed(0)
    model_2 = Net2(params["n_clusters"])
    torch.manual_seed(0)
    model_3 = Net3(params["n_clusters"])
    kmeans_psc = cluster.KMeans(
        n_clusters=params["n_clusters"], random_state=rng, n_init=10, verbose=False
    )

    l = ["noisy_circles", "noisy_moons", "blobs", "no_structure"]
    if name in l:
        print("net 1")
        model = model_1
    elif name == "varied":
        print("net 2")
        model = model_2
    elif name == "aniso":
        print("net 3")
        model = model_3

    psc = PSC(
        model=model,
        clustering_method=kmeans_psc,
        sampling_ratio=0,
        n_components=params["n_clusters"],
        n_neighbor=params["n_neighbors"],
        batch_size_data=10000,
        random_state=rng,
    )

    clustering_algorithms = (
        ("KMeans", KMeans),
        ("SpectralClustering", spectral),
        ("PSC", psc),
    )

    for algo_name, algorithm in clustering_algorithms:
        t0 = time.time()

        # catch warnings related to kneighbors_graph
        with warnings.catch_warnings():
            warnings.filterwarnings(
                "ignore",
                message="the number of connected components of the "
                + "connectivity matrix is [0-9]{1,2}"
                + " > 1. Completing it to avoid stopping the tree early.",
                category=UserWarning,
            )
            warnings.filterwarnings(
                "ignore",
                message="Graph is not fully connected, spectral embedding"
                + " may not work as expected.",
                category=UserWarning,
            )
            algorithm.fit(X)

        t1 = time.time()
        if hasattr(algorithm, "labels_"):
            y_pred = algorithm.labels_.astype(np.int32)
        else:
            y_pred = algorithm.predict(X)

        if algo_name == "PSC":
            path = "JSS_Experiments/Synthesis_dataset/" + str(name) + "2.pth"
            algorithm.save_model(path=path)

        plt.subplot(len(datasets), len(clustering_algorithms), plot_num)
        if i_dataset == 0:
            plt.title(algo_name, size=10)

        colors = np.array(
            list(
                islice(
                    cycle(
                        [
                            "#377eb8",
                            "#ff7f00",
                            "#4daf4a",
                            "#f781bf",
                            "#a65628",
                            "#984ea3",
                            "#999999",
                            "#e41a1c",
                            "#dede00",
                        ]
                    ),
                    int(max(y_pred) + 1),
                )
            )
        )
        # add black color for outliers (if any)
        colors = np.append(colors, ["#000000"])
        plt.scatter(X[:, 0], X[:, 1], s=10, color=colors[y_pred])

        plt.xlim(-2.5, 2.5)
        plt.ylim(-2.5, 2.5)
        plt.xticks(())
        plt.yticks(())
        # plt.text(.99, .01, ('%.2fs' % (t1 - t0)).lstrip('0'),
        #          transform=plt.gca().transAxes, size=12,
        #          horizontalalignment='right')
        plot_num += 1
plt.savefig("synthesis.pdf", format="pdf", bbox_inches="tight")
plt.show()
