__author__ = 'chrisPiemonte'

import itertools
import numpy as np
import matplotlib.pyplot as plt
import rdflib.plugins.sparql as sparql

import plotly.plotly as py, plotly.graph_objs as go
from plotly.graph_objs import *


get_mid = lambda uri: uri.replace("http://rdf.freebase.com/ns", "")

def get_sequences(filename, sep=" ", min_len=1):
    for line in open(filename, "r"):
        sequence = line.split(sep)
        # tofix -> removing the \n at the end of the line
        sequence[-1] = sequence[-1].replace("\n", "")
        if len(sequence) >= min_len:
            yield sequence
            
def scatter_plot(two_dim_vecs, word_labels=None, colors="#00897B", user="chrispolo", api_key="89nned6csl"):
    py.sign_in(user, api_key)

    x_coord = two_dim_vecs[:, 0]
    y_coord = two_dim_vecs[:, 1]

    trace = go.Scattergl(
        x = x_coord, #
        y = y_coord, #
        mode = 'markers',
        text = word_labels, #
        marker = dict(
            color = colors,
            line = dict(width = 1)
        )
    )

    data = [trace]
    return data

def get_types(resource, graph):
    prep_query = sparql.prepareQuery("""
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        SELECT ?type
        WHERE { 
          ?resource rdf:type ?type .
        }
    """)
    resource = rdflib.URIRef(resource)
    return graph.query(prep_query, initBindings={'resource': resource})

def get_color(n):
    #         1.orange,  2.fuchsia, 3.yellow,  4.lgt-blue, 5.green,  6.blue,    7.white,   8.violet
    colors = ["#FF8F00", "#F50057", "#FFFF00", "#00E5FF", "#76FF03", "#2979FF", "#FFFFFF", "#9C27B0"]
    color = ""
    if n < 0:
        color = "#009688" # noise
    elif n < len(colors):
        color = colors[n]
    else:
        color = "#" + format(n**5, '06X')
    return color


# ---------------------------------------------------------


def is_person(uri, mid2types):
    result = False
    mid = get_mid(uri)
    types = mid2types[mid]
    if  "<http://dbpedia.org/ontology/Person>" in types and \
        "<http://dbpedia.org/ontology/Place>" not in types and \
        "<http://dbpedia.org/ontology/Event>" not in types:
        result = True
    return result

def is_agent(uri, mid2types):
    result = False
    mid = get_mid(uri)
    types = mid2types[mid]
    if  "<http://dbpedia.org/ontology/Agent>" in types and \
        "<http://dbpedia.org/ontology/Place>" not in types and \
        "<http://dbpedia.org/ontology/Event>" not in types:
        result = True
    return result

def is_place(uri, mid2types):
    result = False
    mid = get_mid(uri)
    types = mid2types[mid]
    if  "<http://dbpedia.org/ontology/Place>" in types and \
        "<http://dbpedia.org/ontology/Agent>" not in types and \
        "<http://dbpedia.org/ontology/Event>" not in types:
        result = True
    return result

def is_work(uri, mid2types):
    result = False
    mid = get_mid(uri)
    types = mid2types[mid]
    if  "<http://dbpedia.org/ontology/Work>" in types and \
        "<http://dbpedia.org/ontology/Agent>" not in types and \
        "<http://dbpedia.org/ontology/Event>" not in types:
        result = True
    return result

def is_species(uri, mid2types):
    result = False
    mid = get_mid(uri)
    types = mid2types[mid]
    if  "<http://dbpedia.org/ontology/Species>" in types and \
        "<http://dbpedia.org/ontology/Agent>" not in types and \
        "<http://dbpedia.org/ontology/Event>" not in types:
        result = True
    return result

def is_event(uri, mid2types):
    result = False
    mid = get_mid(uri)
    types = mid2types[mid]
    if  "<http://dbpedia.org/ontology/Event>" in types and \
        "<http://dbpedia.org/ontology/Agent>" not in types and \
        "<http://dbpedia.org/ontology/Work>" not in types:
        result = True
    return result

def get_ground_truth(mids, mid2types):
    gt = []
    for mid in mids:
        t = 0
        if is_person(mid, mid2types):  t = 1
        if is_place(mid, mid2types):   t = 2
        if is_work(mid, mid2types):    t = 3
        if is_species(mid, mid2types): t = 4
        if is_event(mid, mid2types):   t = 5
        gt += [t]
    return np.asarray(gt)


# ---------------------------------------------------------



def plot_confusion_matrix(cm, classes,
                          normalize=False,
                          title='Confusion matrix',
                          cmap=plt.cm.Blues):
    """
    This function prints and plots the confusion matrix.
    Normalization can be applied by setting `normalize=True`.
    """
    plt.imshow(cm, interpolation='nearest', cmap=cmap)
    plt.title(title)
    plt.colorbar()
    tick_marks = np.arange(len(classes))
    plt.xticks(tick_marks, classes, rotation=45)
    plt.yticks(tick_marks, classes)

    if normalize:
        cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
        print("Normalized confusion matrix")
    else:
        print('Confusion matrix, without normalization')

    print(cm)

    thresh = cm.max() / 2.
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        plt.text(j, i, cm[i, j],
                 horizontalalignment="center",
                 color="white" if cm[i, j] > thresh else "black")

    plt.tight_layout()
    plt.ylabel('True label')
    plt.xlabel('Predicted label')
