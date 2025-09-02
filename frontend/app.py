import streamlit as st
import sys
import os
import logging



import api_client
import ui
from backend.utils.startup_checker import run_frontend_startup_checks


def main():
    """Main function to run the Streamlit application."""
    # Run startup checks
    if not run_frontend_startup_checks():
        st.error("A required backend service is not running. Please ensure it is started and refresh the page.")
        st.stop()

    ui.render_ui(api_client)

if __name__ == "__main__":
    main()