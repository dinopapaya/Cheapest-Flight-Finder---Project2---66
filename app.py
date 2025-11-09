"""Streamlit front-end for the Cheapest Flight Finder project."""
import streamlit as st

def main():
    st.set_page_config(page_title="Cheapest Flight Finder", page_icon="✈️")
    st.title("Cheapest Flight Finder")
    st.write("Welcome! This app will help you find the cheapest flights between U.S. airports.")

if __name__ == "__main__":
    main()
