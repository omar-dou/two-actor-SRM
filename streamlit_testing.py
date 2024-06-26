import streamlit as st
import time
import base64
import test as t
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

# if 'counter' not in st.session_state: 
#     st.session_state.counter = 0

# def main():
#     imagelist = ['Instagram_icon.png', 'farm.jpg']

#     if st.button("Begin"):
#         bob = int(st.session_state.counter)
#         loading_text = st.empty()
#         loading_image = st.empty()
#         loading_text.write('Loading...')
#         loading_image.image('/Users/omar/Documents/loaded.gif')
#         time.sleep(2)        
#         loading_text.empty()
#         loading_image.empty()
#         loading_image.image('/Users/omar/Documents/' + imagelist[bob])
        
#         st.session_state.counter += 1
#         if st.session_state.counter >= len(imagelist):
#             st.session_state.counter = 0
#         else:
#             pass

# import streamlit as st
# Define page states
PAGES = {
    "Home": "home",
    "Second Page": "second_page",
    "Third Page": "third_page",
    "Fourth Page": "fourth_page",
    "Next": "next_button"
}

def main():

    # Use columns to organize layout
    col1, col2 = st.columns(2)

    with col1:
        st.header("We are glad to have you here.")
        st.write("""
        This is a place where you will be asked to give some time to aid the environment.
        We hope that is ok with you. Please do enjoy your stay.
        """)

        if st.button("Get Started"):
            st.session_state.page = PAGES["Second Page"]  # Set page state to Second Page upon button click

    with col2:
        st.image("/Users/omar/Documents/loaded.gif", caption="Our Logo")

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

    if st.session_state.page == PAGES["Fourth Page"]:
        fourth_page()

def second_page():
    st.title("Selection Task #1")
    st.write("Please select a topic(s) to test.")

    # Use session state to track selected regions
    if "selected_regions" not in st.session_state:
        st.session_state.selected_regions = []

    # Display region selection checkboxes
    regions = ["Northern Hemisphere", "Southern Hemisphere", "Global Temperature", "Monsoon Levels"]

    for region in regions:
        if st.checkbox(region, key=region):
            if region not in st.session_state.selected_regions:
                st.session_state.selected_regions.append(region)
        else:
            if region in st.session_state.selected_regions:
                st.session_state.selected_regions.remove(region)

    # Display selected regions and "Next Button" if any region is selected
    if st.session_state.selected_regions:
        st.write(f"You selected: {', '.join(st.session_state.selected_regions)}")
        if st.button("Next"):
            st.session_state.page = PAGES["Third Page"]

def third_page():
    st.title("Selection Task #2")
    st.write("Please select a loocation.")
    
    if "tlocations" not in st.session_state:
        st.session_state.tlocations = []

    # Display region selection checkboxes
    test_locations = ["15N", "30N", "60N", "eq", "60S", "30S", "15S"]

    for location in test_locations:
        if st.checkbox(location, key=location):
            if location not in st.session_state.tlocations:
                st.session_state.tlocations.append(location)
        else:
            if location in st.session_state.tlocations:
                st.session_state.tlocations.remove(location)

    # Display selected angle and "Next Button" if an angle is selected
    if st.session_state.tlocations:
        st.write(f"You selected: {', '.join(st.session_state.tlocations)}")
        if st.button("Next"):
            st.session_state.page = PAGES["Fourth Page"]
    t.emipoints = st.session_state.tlocations

def fourth_page():
    st.set_option('deprecation.showPyplotGlobalUse', False)
    st.title("Your Results")
    st.write(f"You selecteed: {', '.join(st.session_state.selected_regions)} and {', '.join(st.session_state.tlocations)}")
    st.write("To be implemented...")
    points = st.session_state.tlocations

    t.setup_plots(points)
    fig = t.graph6()
    st.pyplot(fig)

    #st.title(f"Fip: {fig}")

    # Display the plot using Streamlit
    t.setup_plots(points)
    fig = t.graph1()
    st.pyplot(fig)

    t.setup_plots(points)
    fig = t.graph2()
    st.pyplot(fig)

    t.setup_plots(points)
    fig = t.graph3()
    st.pyplot(fig)

    t.setup_plots(points)
    fig = t.graph4()
    st.pyplot(fig)

    t.setup_plots(points)
    fig = t.graph5()
    st.pyplot(fig)


    st.title(f"Emipoints: {t.emipoints}")


if __name__ == "__main__":
    main()
