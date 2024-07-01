import streamlit as st  # Import Streamlit library
import myclim as mc  # Import custom module myclim
import time  # Import time module for time-related functions
import base64  # Import base64 module for encoding/decoding binary data
import test as t  # Import custom module test

# Function to add background from a local image file
def add_bg_from_local(image_file):
    with open(image_file, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())  # Encode image file to base64

    # Inject CSS to set background image using base64 encoded string
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

# Call function to set background image
add_bg_from_local('/Users/omar/Documents/island.jpg')

# Dictionary defining page names and corresponding identifiers
PAGES = {
    "Home": "home",
    "First Page": "first_page",
    "Second Page": "second_page",
    "Input Page": "input_page",
    "Third Page": "third_page",
    "Fourth Page": "fourth_page",
    "Next": "next_button"
}

# CSS style for custom buttons
button_css = """
<style>
/* Target Streamlit buttons */
div.stButton > button {
    background-color: #81dbcf; /* Blue background */
    border: none; /* Remove borders */
    color: white; /* White text */
    padding: 15px 32px; /* Add some padding */
    text-align: center; /* Center the text */
    text-decoration: none; /* Remove underline */
    display: inline-block; /* Make the container block-level */
    font-size: 16px; /* Increase font size */
    margin: 4px 2px; /* Add some margin */
    cursor: pointer; /* Add a pointer cursor on hover */
    border-radius: 8px; /* Rounded corners */
}

div.stButton > button:hover {
    background-color: #5a9991; /* Darker Blue on hover */
    color: #aaabad; /* Darker white text on hover */
}
</style>
"""

# Add the CSS style to the Streamlit app
st.markdown(button_css, unsafe_allow_html=True)

# Main function
def main():
    # Use columns to organize layout
    col1, col2 = st.columns(2)

    with col1:
        st.header("Climate Simulator")
        st.write("""
        Click get started to begin your simulation
        """)
        st.markdown(button_css, unsafe_allow_html=True)
        if st.button("Get Started"):
            st.session_state.page = PAGES["First Page"]  # Set page state to First Page upon button click

    with col2:
        st.image("/Users/omar/Documents/Logo_Sorbonne_Université.png")  # Display an image in the second column

    # Sidebar with more information

    # Handle page navigation based on state
    if "page" not in st.session_state:
        st.session_state.page = PAGES["Home"]  # Default to Home page

    if st.session_state.page == PAGES["First Page"]:
        first_page()

    if st.session_state.page == PAGES["Second Page"]:
        second_page()

    if st.session_state.page == PAGES["Input Page"]:
        input_page()

    if st.session_state.page == PAGES["Third Page"]:
        third_page()

    if st.session_state.page == PAGES["Fourth Page"]:
        fourth_page()

# Function for the first page
def first_page():
    st.title("Selection Task #1")
    st.write("Please choose your preferred number of actors")

    if "selected_actor" not in st.session_state:
        st.session_state.selected_actor = None

    actors = ["1 Actor", "2 Actors", "3 Actors"]
    selected_actor = st.radio("Please choose your preferred amount of actors", actors)

    if selected_actor:
        st.session_state.selected_actor = selected_actor
        st.session_state.selected_actor_count = int(selected_actor.split()[0])
        st.session_state.current_actor_index = 1
        st.session_state.results = []

        if st.button("Next", key="start_button"):  # Unique key for the button
            st.session_state.page = PAGES["Second Page"]

# Function for the second page
def second_page():
    st.title(f"Selection Task #2 for Actor {st.session_state.current_actor_index}")
    st.write("Please select an area of focus")

    if "selected_region" not in st.session_state:
        st.session_state.selected_region = None

    regions = ["NHST", "SHST", "GMST", "monsoon"]
    selected_region = st.radio("Regions", options=regions, key=f"region_actor_{st.session_state.current_actor_index}")

    st.session_state.selected_region = selected_region

    if st.session_state.selected_region:
        st.write(f"You selected: {st.session_state.selected_region}.")
        if st.button("Next", key=f"next_button_{st.session_state.current_actor_index}"):  # Unique key for the button
            st.session_state.page = PAGES["Input Page"]

# Function for the input page
def input_page():
    st.title(f"Selection Task #3 for Actor {st.session_state.current_actor_index}")
    if "set_num" not in st.session_state:
        st.session_state.set_num = None

    set_num = st.text_input(
        "Please enter a setpoint (Press enter to apply)",
        "0.0",
        key=f"set_actor_{st.session_state.current_actor_index}",
    )
    set_num = float(set_num)
    st.session_state.set_num = set_num
    if st.button("Next", key=f"next_button_{st.session_state.set_num}"):  # Unique key for the button
        st.session_state.page = PAGES["Third Page"]

# Function for the third page
def third_page():
    st.title(f"Selection Task #4 for Actor {st.session_state.current_actor_index}")
    st.write("Please select a location")

    if "tlocations" not in st.session_state:
        st.session_state.tlocations = []

    test_locations = ["15N", "30N", "eq", "30S", "15S"]

    for location in test_locations:
        if st.checkbox(location, key=location):
            if location not in st.session_state.tlocations:
                st.session_state.tlocations.append(location)
        else:
            if location in st.session_state.tlocations:
                st.session_state.tlocations.remove(location)

    if st.button("Next", key=f"next_button_fourth_page_{st.session_state.current_actor_index}"):
        result = {
            "actor": st.session_state.current_actor_index,
            "regions": st.session_state.selected_region,
            "setpoint": st.session_state.set_num,
            "epoints": st.session_state.tlocations
        }
        st.session_state.results.append(result)

        if st.session_state.current_actor_index < st.session_state.selected_actor_count:
            st.session_state.current_actor_index += 1
            st.session_state.selected_region = []  # Reset selected regions for next actor
            st.session_state.selected_angle = None  # Reset selected angle for next actor
            st.session_state.page = PAGES["Second Page"]
        else:
            st.session_state.page = PAGES["Fourth Page"]

# Function for the fourth page
def fourth_page():
    st.set_option('deprecation.showPyplotGlobalUse', False)
    st.title("Your Results:")

    # Accessing results for the first actor
    act1 = st.session_state.results[0]
    actnums = act1['actor']
    region1 = act1['regions']
    set1 = act1['setpoint']
    points1 = act1['epoints']

    # Handling subsequent actors if available
    if len(st.session_state.results) > 1:
        act2 = st.session_state.results[1]
        actnums = act2['actor']
        region2 = act2['regions']
        points2 = act2['epoints']
        set2 = act2['setpoint']

        if len(st.session_state.results) > 2:
            act3 = st.session_state.results[2]
            actnums = act3['actor']
            region3 = act3['regions']
            points3 = act3['epoints']
            set3 = act3['setpoint']

    # Depending on the number of actors, call the appropriate setup function from module t
    if actnums == 3:
        P = t.setup_actor3(region1, set1, points1, region2, set2, points2, region3, set3, points3)
    elif actnums == 2:
        P = t.setup_actor2(region1, set1, points1, region2, set2, points2)
    else:
        P = t.setup_actor1(region1, set1, points1)

    # Display various graphs using functions from module t
    t.setup_plots(P)
    fig = t.graph1()
    st.pyplot(fig)

    t.setup_plots(P)
    fig = t.graph2()
    st.pyplot(fig)

    t.setup_plots(P)
    fig = t.graph3(P)
    st.pyplot(fig)

    t.setup_plots(P)
    fig = t.graph4()
    st.pyplot(fig)

    t.setup_plots(P)
    fig = t.graph5()
    st.pyplot(fig)

    t.setup_plots(P)
    fig = t.graph6()
    st.pyplot(fig)

# Entry point of the script
if __name__ == "__main__":
    main()
