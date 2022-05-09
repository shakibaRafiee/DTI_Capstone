import streamlit as st
import dill

st.title('RunLikeU')

@st.cache(allow_output_mutation=True)
def load_graph():
    graph = dill.load(open('DTI_Capstone/San_Francisco/temp_graph.pkd', 'rb'))
    return graph

graph = load_graph()
