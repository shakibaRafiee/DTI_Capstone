import streamlit as st
import dill

import osmnx as ox

################################################## function ###################################################

@st.cache(allow_output_mutation=True)
def load_graph():
    graph = dill.load(open('./San_Francisco/SanFrancisco_prediction_Graph.pkd', 'rb'))
    return graph

###############################################################################################################

st.title('RunLikeU')

graph = load_graph()

################################################# User Inputs ##################################################

# Get street address as text_input
address = st.text_input('Start Location', 'Haight-Ashbury, San Francisco, CA, USA')
st.write('The current start location is', address)

address_state = st.text('Finding location...')

# find the origin node index
G_simple = ox.graph_from_address(address, dist=50, network_type='walk')
orig = list(G_simple.nodes)[0]

address_state.text("Found the address!")

# Get running distance as number_input
Running_length = st.number_input(label = 'Desired Running Distance (in miles)', min_value = 0.5, value = 3.0, step = 0.5, format="%.1f")
st.write('The current desired running distance is', Running_length, 'miles')
# convert running distanc to m
Running_Dist = Running_length * 1.60934 * 1000 / 2

################################################# find routes ##################################################
