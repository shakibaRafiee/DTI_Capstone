import streamlit as st
import dill

st.title('RunLikeU')

@st.cache(allow_output_mutation=True)
def load_graph():
    graph = dill.load(open('./San_Francisco/SanFrancisco_prediction_Graph.pkd', 'rb'))
    return graph

graph = load_graph()
