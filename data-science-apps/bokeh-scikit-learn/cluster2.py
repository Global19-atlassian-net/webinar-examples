import numpy as np
import matplotlib.pyplot as plt

from sklearn import cluster, datasets
from sklearn.neighbors import kneighbors_graph
from sklearn.preprocessing import StandardScaler

from bokeh.plotting import Figure
from bokeh.palettes import Spectral6
from bokeh.models.widgets import VBox, HBox, Select, Slider

from bokeh.models import ColumnDataSource
from bokeh.io import curdoc

# SET UP DATA
np.random.seed(0)
n_samples = 1500

# Noisy circles dataset
X, y = datasets.make_circles(n_samples=n_samples, factor=.5, noise=.05)
# normalize dataset for easier parameter selection
X = StandardScaler().fit_transform(X)
# estimate bandwidth for mean shift
bandwidth = cluster.estimate_bandwidth(X, quantile=0.3)
# connectivity matrix for structured Ward
connectivity = kneighbors_graph(X, n_neighbors=10, include_self=False)
# make connectivity symmetric
connectivity = 0.5 * (connectivity + connectivity.T)

spectral = np.hstack([Spectral6] * 20)
colors = [spectral[i] for i in y]

source = ColumnDataSource(data=dict(x=X[:, 0], y=X[:, 1], colors=colors))

# SET UP PLOT
algorithm = 'MiniBatchKMeans'
dataset = 'Noisy Circles'

plot = Figure(plot_width=400, plot_height=400, title=None,
              title_text_font_size='10pt', toolbar_location=None)
plot.circle('x', 'y', fill_color='colors', line_color=None, source=source)
plot.xgrid[0].grid_line_color=None
plot.ygrid[0].grid_line_color=None

# SET UP WIDGETS
clustering_algorithms= ['MiniBatchKMeans', 'AffinityPropagation', 
    'MeanShift', 'SpectralClustering', 'Ward', 'AgglomerativeClustering',
    'DBSCAN', 'Birch']

datasets_names = ['Noisy Circles', 'Noisy Moons', 'Blobs', 'No Structure']

algorithm_select = Select(value='MiniBatchKMeans', title='Select algorithm:', options=clustering_algorithms)
dataset_select = Select(value='Noisy Circles', title='Select dataset:', options=datasets_names)

samples_slider = Slider(title="Number of samples", value=1500.0, start=1000.0, end=3000.0, step=100)
clusters_slider = Slider(title="Number of clusters", value=2.0, start=2.0, end=10.0, step=1)


def clustering(X, algorithm, n_clusters):
    # normalize dataset for easier parameter selection
    X = StandardScaler().fit_transform(X)
    # estimate bandwidth for mean shift
    bandwidth = cluster.estimate_bandwidth(X, quantile=0.3)
    # connectivity matrix for structured Ward
    connectivity = kneighbors_graph(X, n_neighbors=10, include_self=False)
    # make connectivity symmetric
    connectivity = 0.5 * (connectivity + connectivity.T)
    # Generate the new colors:
    if algorithm=='MiniBatchKMeans':
        model = cluster.MiniBatchKMeans(n_clusters=n_clusters)
    elif algorithm=='AffinityPropagation':
        model = cluster.AffinityPropagation(damping=.9, preference=-200)
    elif algorithm=='MeanShift':
        model = cluster.MeanShift(bandwidth=bandwidth, bin_seeding=True)
    elif algorithm=='SpectralClustering':
        model = cluster.SpectralClustering(n_clusters=n_clusters,
                                          eigen_solver='arpack',
                                          affinity="nearest_neighbors")
    elif algorithm=='Ward':
        model = cluster.AgglomerativeClustering(n_clusters=n_clusters, linkage='ward',
                                           connectivity=connectivity)
    elif algorithm=='AgglomerativeClustering':
        model = cluster.AgglomerativeClustering(
            linkage="average", affinity="cityblock", n_clusters=n_clusters,
            connectivity=connectivity)
    elif algorithm=='Birch':
        model = cluster.Birch(n_clusters=n_clusters)
    elif algorithm=='DBSCAN':
        model = cluster.DBSCAN(eps=.2)
    else:
        print('No Algorithm selected. Default is MiniBatchKMeans')
        model = cluster.MiniBatchKMeans(n_clusters=n_clusters)
    model.fit(X)

    if hasattr(model, 'labels_'):
            y_pred = model.labels_.astype(np.int)
    else:
            y_pred = model.predict(X)

    return X, y_pred

def get_dataset(dataset, n_samples):
    # Generate the new data:
    if dataset=='Noisy Circles':
        X, y = datasets.make_circles(n_samples=n_samples, factor=.5, noise=.05)
    elif dataset=='Noisy Moons':
        X, y = datasets.make_moons(n_samples=n_samples, noise=.05)
    elif dataset=='Blobs':
        X, y = datasets.make_blobs(n_samples=n_samples, random_state=8)
    else:
        X, y = np.random.rand(n_samples, 2), None

    return X, y

# SET UP CALLBACKS
def update_algorithm(attrname, old, new):

    # Get the drop down values
    algorithm = algorithm_select.value
    n_clusters = int(clusters_slider.value)
    global X, y

    X, y_pred = clustering(X, algorithm, n_clusters)
    colors = [spectral[i] for i in y_pred]

    source.data['colors'] = colors
    source.data['x'] = X[:, 0]
    source.data['y'] = X[:, 1]

    plot.title = algorithm

def update_dataset(attrname, old, new):

    # Get the drop down values
    dataset = dataset_select.value
    algorithm = algorithm_select.value
    n_clusters = int(clusters_slider.value)
    n_samples = int(samples_slider.value)
    global X, y

    # Generate the new data:
    X, y = get_dataset(dataset, n_samples)

    X, y_pred = clustering(X, algorithm, n_clusters)
    colors = [spectral[i] for i in y_pred]

    source.data['x'] = X[:, 0]
    source.data['y'] = X[:, 1]
    source.data['colors'] = colors

def update_samples(attrname, old, new):
    dataset = dataset_select.value
    algorithm = algorithm_select.value
    n_clusters = int(clusters_slider.value)
    n_samples = int(samples_slider.value)

    X, y = get_dataset(dataset, n_samples)
    X, y_pred = clustering(X, algorithm, n_clusters)
    colors = [spectral[i] for i in y_pred]

    source.data['x'] = X[:, 0]
    source.data['y'] = X[:, 1]
    source.data['colors'] = colors

def update_clusters(attrname, old, new):
    algorithm = algorithm_select.value
    n_clusters = int(clusters_slider.value)
    n_samples = int(samples_slider.value)

    global X
    X, y_pred = clustering(X, algorithm, n_clusters)
    colors = [spectral[i] for i in y_pred]

    source.data['x'] = X[:, 0]
    source.data['y'] = X[:, 1]
    source.data['colors'] = colors

algorithm_select.on_change('value', update_algorithm)
dataset_select.on_change('value', update_dataset)
clusters_slider.on_change('value', update_clusters)
samples_slider.on_change('value', update_samples)

# SET UP LAYOUT
sliders = VBox(children=[samples_slider, clusters_slider])
selects = HBox(children=[dataset_select, algorithm_select])
inputs = VBox(children=[sliders, selects])
plots = HBox(children=[plot])
# add to document
curdoc().add_root(HBox(children=[inputs, plots]))