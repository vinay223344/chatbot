import streamlit as st
from rdflib import Graph, Namespace, RDF, RDFS, OWL, Literal
import re

# -------------------------------
# Load RDF/OWL Knowledge Graph
# -------------------------------
g = Graph()
g.parse("faculty1.ttl", format="turtle")

# Define namespace
RVR = Namespace("http://www.rvrjc.ac.in/faculty#")

# -------------------------------
# Streamlit UI
# -------------------------------
st.set_page_config(page_title="Faculty KG Chatbot", layout="centered")
st.title("🎓 Faculty Knowledge Graph Chatbot")
st.caption("Ask questions about professors, research areas, and publications!")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# -------------------------------
# Helper function: SPARQL Queries
# -------------------------------
def query_kg(query_str):
    qres = g.query(query_str)
    return [str(row[0]) for row in qres]

# -------------------------------
# Process user input
# -------------------------------
user_input = st.chat_input("Ask about faculty or research...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    # -------------------------------
    # Simple NLP + Rule-based Intent Matching
    # -------------------------------
    response = "Sorry, I couldn’t find any information about that."

    text = user_input.lower()

    # 1️⃣ Ask about professors in a department
    dept_match = re.search(r"department of ([a-z ]+)", text)
    if dept_match:
        dept_name = dept_match.group(1).title()
        query = f"""
        SELECT ?name WHERE {{
            ?x rdf:type rvr:Professor .
            ?x rvr:worksInDepartment "{dept_name}" .
            ?x rvr:hasName ?name .
        }}
        """
        res = query_kg(query)
        if res:
            response = f"Professors in Department of {dept_name}: " + ", ".join(res)
        else:
            response = f"No professors found in Department of {dept_name}."

    # 2️⃣ Ask about research areas of a professor
    elif "research" in text or "area" in text:
        name_match = re.search(r"(?:professor|dr\.?) ([a-z ]+)", text)
        if name_match:
            prof_name = name_match.group(1).title()
            query = f"""
            SELECT ?area WHERE {{
                ?x rdf:type rvr:Professor .
                ?x rvr:hasName "{prof_name}" .
                ?x rvr:hasResearchArea ?area .
            }}
            """
            res = query_kg(query)
            if res:
                response = f"Research areas of {prof_name}: " + ", ".join(res)
            else:
                response = f"No research area found for {prof_name}."

    # 3️⃣ Ask about publications of a professor
    elif "publication" in text:
        name_match = re.search(r"(?:professor|dr\.?) ([a-z ]+)", text)
        if name_match:
            prof_name = name_match.group(1).title()
            query = f"""
            SELECT ?pub WHERE {{
                ?x rdf:type rvr:Professor .
                ?x rvr:hasName "{prof_name}" .
                ?x rvr:hasPublication ?pub .
            }}
            """
            res = query_kg(query)
            if res:
                response = f"Publications by {prof_name}: " + ", ".join(res)
            else:
                response = f"No publications found for {prof_name}."

    # 4️⃣ Ask about PhD students guided by a professor
    elif "phd" in text or "student" in text or "guide" in text:
        name_match = re.search(r"(?:professor|dr\.?) ([a-z ]+)", text)
        if name_match:
            prof_name = name_match.group(1).title()
            query = f"""
            SELECT ?student WHERE {{
                ?x rdf:type rvr:Professor .
                ?x rvr:hasName "{prof_name}" .
                ?x rvr:guides ?student .
            }}
            """
            res = query_kg(query)
            if res:
                response = f"{prof_name} has guided: " + ", ".join(res)
            else:
                response = f"No students found for {prof_name}."

    # Save assistant response
    st.session_state.messages.append({"role": "assistant", "content": response})

    # Display assistant message
    with st.chat_message("assistant"):
        st.markdown(response)
