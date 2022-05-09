import streamlit as st
import dill

import networkx as nx
import osmnx as ox

################################################## function ###################################################

@st.cache(allow_output_mutation=True)
def load_graph():
    graph = dill.load(open('./San_Francisco/SanFrancisco_prediction_Graph.pkd', 'rb'))
    return graph

def weighted_sum(point1, point2, atr):
    # normalize the populairy by multiplying by length and also factor other features
    return  atr[0]['length']*0.01 + 2*(2*(1-atr[0]['RF_model_pred_sg'])*(atr[0]['length'])/100)

def find_optimal_path_in_range():
    # Find routes with minimum badness to the chosen destination nodes in range of orig
    Min_badness_inRange = { key: Min_badness[key] for key in Destination_nodes}

    # Find and filter acceptable target points in range of desired distance
    Final_Destination_nodes =[key for key, value in Min_badness_inRange.items() if value ==min(Min_badness_inRange.values())]

    return Final_Destination_nodes

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
