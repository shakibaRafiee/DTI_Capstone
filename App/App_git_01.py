import streamlit as st
from PIL import Image
import dill

import networkx as nx
import osmnx as ox

import folium
from streamlit_folium import folium_static

################################################## function ####################################################

@st.cache(allow_output_mutation=True)
def load_graph():
    #graph = dill.load(open('./San_Francisco/SanFrancisco_prediction_Graph.pkd', 'rb'))
    graph = dill.load(open('./San_Francisco/SanFrancisco_prediction_Graph_capped20.pkd', 'rb'))

    return graph

def weighted_sum(point1, point2, atr):
    # normalize the costs
    pop_cost    = 1 - (atr[0]['popularity_pred'])*0.05
    parks_cost  = 1 - (atr[0]['parks_recs'])
    lights_cost =     (atr[0]['trafic signals'])*0.5
    safty_cost  =     (atr[0]['crime'])
    length_cost =     (atr[0]['length'])/2775

    # normalize the populairy by multiplying by length
    w_l = (atr[0]['length'])/2775 # length weight

    return  length_cost + w_l*(pop_cost + ((w_parks**2)*parks_cost) + ((w_lights**2)*lights_cost) + ((w_safety**2)*safty_cost))

def find_optimal_path_in_range():
    # Find routes with minimum badness to the chosen destination nodes in range of orig
    Min_badness_inRange = { key: Min_badness[key] for key in Destination_nodes}

    # Find and filter acceptable target points in range of desired distance
    Final_Destination_nodes =[key for key, value in Min_badness_inRange.items() if value ==min(Min_badness_inRange.values())]

    return Final_Destination_nodes

def find_route(dest):
    while True:
        # find the path to dest that minimises length
        route_1 = nx.shortest_path(graph, orig, dest, weight=weighted_sum)

        # revise the graph and remove edges
        graph2 = graph.copy()
        edges_to_remove = [(u,v) for (u,v,edg) in graph2.edges(data=True) if (u in route_1[2:-2] or v in route_1[2:-2])]
        graph2.remove_edges_from(edges_to_remove)

        # find the path from dest that minimizes badness
        try:
            route_2 = nx.shortest_path(graph2, dest, orig, weight=weighted_sum)
            break
        except nx.NetworkXNoPath:
            print('No path, lets try again')

        Destination_nodes.remove(dest)
        dest = find_optimal_path_in_range()[0]
        find_route(dest)

    graph2.add_edges_from(edges_to_remove)
    for edge in edges_to_remove:
        graph.add_edge(*edge, key=0, popularity_pred = graph.get_edge_data(*edge)[0]['popularity_pred']-3)
    # route
    Cycle = route_1+route_2[1:-1]

    # update the graph to discourage repetittion
    edges_to_update = [(u,v) for (u,v,edg) in graph2.edges(data=True) if (u in Cycle[2:-2] or v in Cycle[2:-2])]

    return Cycle, dest

def update_destination_nodes(Destination_nodes, dest):
    distance_to_dist = nx.shortest_path_length(graph, dest, weight='length')
    destinations_to_remove = [key for key, val in distance_to_dist.items() if val<200]
    Destination_nodes = list(filter(lambda x: x not in destinations_to_remove, Destination_nodes))
    return Destination_nodes

def folium_plot(Cycle, dest):
    Location_orig= [graph.nodes[orig]['y'], graph.nodes[orig]['x']]
    Location_dest= [graph.nodes[dest]['y'], graph.nodes[dest]['x']]

    length      = nx.path_weight(graph, Cycle, weight="length")/(1.60934 * 1000)
    crime_index = nx.path_weight(graph, Cycle, weight="crime")/length
    cross       = nx.path_weight(graph, Cycle, weight="trafic signals")

    html_orig=  f"""
                <p> <b> <small> Start Point </small> </b> </p>
                <p> <small> route Length:{length:.2f} miles </small> </p>
                <p> <small> Crime Index:{crime_index:.2f} </small> </p>
                <p> <small> Traffic Signals: {int(cross/2):.0f} </small> </p>
                """

    html_dest=  f"""
                <p> <b> <small> Destination Point </small> </b> </p>
                <p> <small> route Length:{length:.2f} miles </small> </p>
                <p> <small> Crime Index:{crime_index:.2f} </small> </p>
                <p> <small> Traffic Signals: {int(cross/2):.0f} </small> </p>
                """

    iframe_orig = folium.IFrame(html=html_orig, width=150, height=150)
    popup_orig  = folium.Popup(iframe_orig, max_width=150)

    iframe_dest = folium.IFrame(html=html_dest, width=150, height=150)
    popup_dest  = folium.Popup(iframe_dest, max_width=150)

    marker_orig = folium.Marker(location = Location_orig, popup = popup_orig, icon = folium.Icon(color='red'))
    marker_dest = folium.Marker(location = Location_dest, popup = popup_dest, icon = folium.Icon(color='red'))

    cycle_graph_map = ox.plot_route_folium(graph, Cycle, color='lightgreen',opacity=0.8, weight=8)

    marker_orig.add_to(cycle_graph_map)
    #marker_dest.add_to(cycle_graph_map)

    return cycle_graph_map
###############################################################################################################

st.title('RunLikeU')
graph_orig = load_graph()

################################################# User Inputs ##################################################

with st.sidebar:
    image = Image.open('./App/logo_sidebar.png')
    col1, col2, col3 = st.columns([1,5,1])
    with col2:
        st.image(image)


    # Get street address as text_input
    #address = st.text_input('Start Location (currently only avaiable in San Francisco)', 'Haight-Ashbury, San Francisco, CA, USA')
    st.markdown('Currently only avaiable in San Francisco')
    address = st.text_input('Start Location', 'Market & 7th street, San Francisco, CA')

    # find the origin node index
    G_simple = ox.graph_from_address(address, dist=50, network_type='walk')
    orig = list(G_simple.nodes)[0]

    # Get running distance as number_input
    Running_length = st.number_input(label = 'Desired Running Distance (in miles)', min_value = 0.5, value = 3.0, step = 0.5, format="%.1f")
    # convert running distanc to m
    Running_Dist = Running_length * 1.60934 * 1000 / 2

    st.markdown("Priorities")

    w_safety   = st.slider('How much do you prioritize safty of the route?', 0, 10, 7)
    w_parks    = st.slider('How much do you prioritize the green space?', 0, 10, 5)
    w_lights   = st.slider('How much do you prioritize avoiding traffic lights?', 0, 10, 5)

st.write('The current start location is', address)
st.write('The current desired running distance is', Running_length, 'miles')

if st.button('Find Routes'):
     graph = graph_orig.copy()
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
     Cycle1, dest1 = find_route(dest1)
     cycle_graph_map1 = folium_plot(Cycle1, dest1)
     folium_static(cycle_graph_map1,height= 300)
     route1_state.text('Found a great route :)')
     ################################################# find route2 ##################################################
     route2_state = st.text('Finding routes...')
     Destination_nodes = update_destination_nodes(Destination_nodes, dest1)
     dest2 = find_optimal_path_in_range()[0]
     Cycle2, dest2 = find_route(dest2)
     cycle_graph_map2 = folium_plot(Cycle2, dest2)
     folium_static(cycle_graph_map2, height= 300)
     route2_state.text("Here's another route")
     ################################################# find route3 ##################################################
     route3_state = st.text('Finding routes...')
     Destination_nodes = update_destination_nodes(Destination_nodes, dest2)
     dest3 = find_optimal_path_in_range()[0]
     Cycle3, dest3 = find_route(dest3)
     cycle_graph_map3 = folium_plot(Cycle3, dest3)
     folium_static(cycle_graph_map3, height= 300)
     route3_state.text("How about this one?")
