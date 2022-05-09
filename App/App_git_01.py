import streamlit as st
import dill

import osmnx as ox

st.title('RunLikeU')

@st.cache(allow_output_mutation=True)
def load_graph():
    graph = dill.load(open('./San_Francisco/SanFrancisco_prediction_Graph.pkd', 'rb'))
    return graph

graph = load_graph()

# Get street address as text_input
address = st.text_input('Start Location', 'Haight-Ashbury, San Francisco, CA, USA')
st.write('The current start location is', address)

address_state = st.text('Finding location...')

# find the origin node index
G_simple = ox.graph_from_address(address, dist=50, network_type='walk')
orig = list(G_simple.nodes)[0]
