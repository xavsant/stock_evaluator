# Imports
import streamlit as st

# Mock backend function
def backend_function(variable):
    return f"Data sent to backend: {variable}"

def sidebar():
    st.sidebar.title("Input Variables")

    stock = st.sidebar.selectbox("Select Stock:", options = ['AAPL', 'TSLA', 'NVDA'],)
    
    generate_button = st.sidebar.button("Generate")

    if generate_button:
        result = backend_function([stock])
        st.write(result)

# Layout for the application
def main():
    st.header("Sentiment Analysis")
    st.markdown("For a chosen stock, this function searches Yahoo Finance for the latest news and  \n  \
                gets the latest sentiment (individual + overall) using a trained model.  \n  \
                Select your variables in the column on the left.")
    "---"

    st.write("### Output")
    sidebar()
    
if __name__ == "__page__":
    main()
