import streamlit as st
import streamlit.components.v1 as components
from streamlit_agraph import agraph, Node, Edge, Config
import networkx as nx
import glob
import matplotlib.pyplot as plt
import math
import igraph

plt.rcParams.update({'text.color': "red",
                     'axes.labelcolor': "red"})

st.set_page_config(layout="wide")
st.title("Graph Viewer")

def freq_to_display(fmin, fmax, G):

    filtered_edges = []
    for u, v, freq in G.edges(data='freq'):
        if freq >= fmin and freq <= fmax:
            filtered_edges.append((u, v))
    filtered_G = G.edge_subgraph(filtered_edges)
    return filtered_G

sidebar = st.sidebar
# print(glob.glob('stats/sch/G*'))
# select method from list of methods
take = sidebar.selectbox('Select a take', [x[10:] for x in glob.glob('stats/sch/G*')])
fmin, fmax = st.slider('Select a frequency range', 1, 45, (1, 45), step=1)
edge_scale = st.slider('Select edge weight', 0.0, 20.0, 8.5, step=0.1)

schizo_list_g = glob.glob(f'stats/sch/{take}/*')
control_list_g = glob.glob(f'stats/control/{take}/*')

schizo_list_g_names = [x.split('/')[3][15:] for x in schizo_list_g]
control_list_g_names = [x.split('/')[3][15:] for x in control_list_g]

if sidebar.checkbox('Schizophrenia'):
    schizo_subject = sidebar.radio('Select a subject (Schizophrenia)', schizo_list_g_names)
    G = nx.read_gpickle(schizo_list_g[schizo_list_g_names.index(schizo_subject)])
else:
    control_subject = sidebar.radio('Select a subject (Control)', control_list_g_names)
    G = nx.read_gpickle(control_list_g[control_list_g_names.index(control_subject)])

# check if G is instance of list
if isinstance(G, list):

    t_epoch = st.slider('Select a epoch', 0, len(G), 5, step=1)
    print(G[t_epoch].to_networkx())
    g_vis = freq_to_display(fmin, fmax, G[t_epoch].to_networkx())
else:
    g_vis = freq_to_display(fmin, fmax, G)


filtered_G = g_vis

nodes = []
pos = dict(x=[], y=[])
for n in filtered_G.nodes():
    node_attrs = filtered_G.nodes[n]
    node_id = str(n)
    node_label = node_attrs['label']
    node_coords = node_attrs['coords']
    node_degree = node_attrs['degree']
    node_motif = node_attrs['motif']
    node = Node(id=node_id, label=node_label, x=node_coords[0]*1000, y=node_coords[1]*1000, title=f"Degree: {node_degree}\nMotif: {node_motif}", shape='circle', color='#FFFFFF', font={'size': 20+node_degree*2})
    nodes.append(node)

edges = []
for u, v, edge_attrs in filtered_G.edges(data=True):
    edge_id = str(u) + '-' + str(v)
    edge_label = str(edge_attrs['freq'])

    edge_width = edge_attrs.get('weight', 1.0)
    # scale edge width exponentially
    edge_width = 1 / (1 + math.exp(-edge_width))*edge_scale
    # edge_width = 1 / (1 + math.exp(-edge_attrs.get('weight', 1.0)))
    edge_color = edge_attrs.get('edge_color', '#000000')
    edge = Edge(id=edge_id, source=str(u), target=str(v), label=edge_label, width=edge_width, color=edge_color, smooth=True)
    edges.append(edge)

# Create a Config object to control the layout and appearance of the graph
config = Config(width='100%', height=600, nodeHighlightBehavior=True, highlightColor="#F7A7A6",
                layout={"hierarchical": False}, css=""".vis-network canvas.vis-zoomMove {cursor: not-allowed;}"""
                ,scaling={"label": {"enabled": True}, "min": 10, "max": 50},
                physics={"enabled": True, "stabilization": False, "forceAtlas2Based": {"theta": 0.5, "gravitationalConstant": -50.0, "centralGravity": 0.01, "springLength": 100, "springConstant": 0.08, "damping": 0.4, "avoidOverlap": 0}, "solver": "forceAtlas2Based", "iterations": 10})

# node={'labelProperty': 'label'},
# link={'labelProperty': 'label', 'renderLabel': True}

# Plot the graph using the agraph function
# st.write(agraph(nodes=nodes, edges=edges, config=config))
return_value = agraph(nodes=nodes,
                      edges=edges,
                      config=config)
