import streamlit as st
import dill

import networkx as nx
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

route1_state = st.text('Finding routes...')

# Find the shortest path between origin and all nodes (to disregarad nodes where the shortest path is longer than desired length)
Shortest_Lengths = nx.shortest_path_length(graph, orig, weight='length')
e = 200 # error (in m)
Destination_nodes = [key for key, value in Shortest_Lengths.items() if (Running_Dist-e)< value <(Running_Dist+e/4)]

#Find the path with min badness between origin and all nodes
Min_badness = nx.shortest_path_length(graph, orig, weight=weighted_sum)

Final_Destination_nodes = find_optimal_path_in_range()
dest1 = Final_Destination_nodes[0]

################################################# find route1 ##################################################
