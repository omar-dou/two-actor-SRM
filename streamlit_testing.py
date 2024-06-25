import streamlit as st
import time
import base64

def add_bg_from_local(image_file):
    with open(image_file, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url(data:image/{"jpg"};base64,{encoded_string.decode()});
        background-size: cover
    }}
    </style>
    """,
    unsafe_allow_html=True
    )
add_bg_from_local('/Users/omar/Documents/yemoun.jpg')    

# Define page states
PAGES = {
    "Home": "home",
    "Second Page": "second_page",
    "Third Page": "third_page",
    "Next Button": "next_button"  # Define the Next Button page
}

def main():
    st.title("TEST")




    # Use columns to organize layout
    col1, col2 = st.columns(2)

    with col1:
        st.header("THIS IS A TEST PAGE.")
        st.write("""
        This is a TEST.
        """)

        if st.button("Get Started"):
            st.session_state.page = PAGES["Second Page"]  # Set page state to Second Page upon button click

    with col2:
        st.image('/Users/omar/Documents/Instagram_icon.png')


    if st.button("Begin"):
        loading_text = st.empty()
        loading_image = st.empty()
        loading_text.write('Loading...')
        loading_image.image('/Users/omar/Documents/loaded.gif')
        time.sleep(2)        
        loading_text.empty()
        loading_image.empty()
        loading_image.image('/Users/omar/Documents/farm.jpg')



    else:
        pass





    # Sidebar with more information
    st.sidebar.title("About Us")
    st.sidebar.write("""
    We are a dedicated team trying to aid the world against the battles of climate change.
    Learn more about our mission and values.
    """)

    # Handle page navigation based on state
    if "page" not in st.session_state:
        st.session_state.page = PAGES["Home"]  # Default to Home page

    if st.session_state.page == PAGES["Second Page"]:
        second_page()
    
    if st.session_state.page == PAGES["Third Page"]:
         third_page()

def second_page():
    st.title("Selection Task #1")
    st.write("Please select an area to protect.")

    # Use session state to track if a region button is clicked
    if "region_selected" not in st.session_state:
        st.session_state.region_selected = False

    # Display region selection buttons or selected region
    if not st.session_state.region_selected:
        if st.button("Northern Hemisphere"):
            st.session_state.region_selected = True
            st.session_state.selected_region = "Northern Hemisphere"

        elif st.button("Southern Hemisphere"):
            st.session_state.region_selected = True
            st.session_state.selected_region = "Southern Hemisphere"

        elif st.button("Global Temperature"):
            st.session_state.region_selected = True
            st.session_state.selected_region = "Global Temperature"

        elif st.button("Monsoon Levels"):
            st.session_state.region_selected = True
            st.session_state.selected_region = "Monsoon Levels"

    # Display selected region and "Next Button" if a region is selected
    if st.session_state.region_selected:
        st.write(f"You selected: {st.session_state.selected_region}")
        if st.button("Next Button"):
            st.session_state.page = PAGES["Third Page"]

def third_page():
    st.title("Selection Task #2")
    st.write("Please select an angle.")
    
    # Use session state to track if a region button is clicked
    if "angle_selected" not in st.session_state:
        st.session_state.angle_selected = False

    # Display region selection buttons or selected region
    if not st.session_state.region_selected:
        if st.button("15°N"):
            st.session_state.angle_selected = True
            st.session_state.angle_selected = "Northern Hemisphere"

        elif st.button("30°N"):
            st.session_state.region_selected = True
            st.session_state.selected_region = "Southern Hemisphere"

        elif st.button("60°N"):
            st.session_state.region_selected = True
            st.session_state.selected_region = "Global Temperature"

        elif st.button("15°S"):
            st.session_state.region_selected = True
            st.session_state.selected_region = "Monsoon Levels"

    # Display selected region and "Next Button" if a region is selected
    if st.session_state.region_selected:
        st.write(f"You selected: {st.session_state.selected_region}")
        if st.button("Next Button"):
            st.session_state.page = PAGES["Third Page"]

if __name__ == "__main__":
    main()
