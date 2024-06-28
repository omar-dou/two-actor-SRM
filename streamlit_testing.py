import streamlit as st
import myclim as mc
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
    "First Page": "first_page",
    "Second Page": "second_page",
    "Input Page": "input_page",
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
            st.session_state.page = PAGES["First Page"]  # Set page state to Second Page upon button click

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

def first_page():
    st.title("Selection Task #1")
    st.write("Choose the number of actors participating.")
    if "selected_actor" not in st.session_state:
        st.session_state.selected_actor = None

    actors = ["1 Actor", "2 Actors", "3 Actors"]
    selected_actor = st.radio("How many actors are participating?:", actors)

    if selected_actor:
        st.session_state.selected_actor = selected_actor
        st.session_state.selected_actor_count = int(selected_actor.split()[0])
        st.session_state.current_actor_index = 1
        st.session_state.results = []
        if st.button("Next", key="start_button"):  # Unique key for  the button
            st.session_state.page = PAGES["Second Page"]
#=============================================================================================================================
def second_page():
    st.title(f"Selection Task #2 for Actor {st.session_state.current_actor_index}")
    st.write("Please select one area to protect.")

    if "selected_region" not in st.session_state:
        st.session_state.selected_region = None

    regions = ["NHST", "SHST", "GMST", "monsoon"]

    selected_region = st.radio("Regions", options=regions, key=f"region_actor_{st.session_state.current_actor_index}")

    st.session_state.selected_region = selected_region

    if st.session_state.selected_region:
        st.write(f"You selected: {st.session_state.selected_region}.")
        if st.button("Next", key=f"next_button_{st.session_state.current_actor_index}"):  # Unique key for the button
            st.session_state.page = PAGES["Input Page"]

#title = st.text_input("Movie title", "Life of Brian")

def input_page():
    st.title("Selection Task #3")
    if "set_num" not in st.session_state:
        st.session_state.set_num = None
    
    set_num = st.text_input(
        "Please enter a setpoint",
        "0.0",
        key=f"set_actor_{st.session_state.current_actor_index}",
    )
    set_num = float(set_num)
    st.session_state.set_num = set_num
    if st.session_state.set_num:
        st.write(f"Setppoint: {st.session_state.set_num}.")
        if st.button("Next", key=f"next_button_{st.session_state.set_num}"):  # Unique key for the button
            st.session_state.page = PAGES["Third Page"]



def third_page():
    st.title("Selection Task #3")
    st.write("Please select a loocation.")
    
    if "tlocations" not in st.session_state:
        st.session_state.tlocations = []

    # Display region selection checkboxes
    test_locations = ["15N", "30N", "eq", "30S", "15S"]

    for location in test_locations:
        if st.checkbox(location, key=location):
            if location not in st.session_state.tlocations:
                st.session_state.tlocations.append(location)
        else:
            if location in st.session_state.tlocations:
                st.session_state.tlocations.remove(location)

    # Display selected angle and "Next Button" if an angle is selected
    if st.button("Next", key=f"next_button_fourth_page_{st.session_state.current_actor_index}"):
        # Append current actor's result to results list
        result = {
            "actor": st.session_state.current_actor_index,
            "regions": st.session_state.selected_region,
            "setpoint": st.session_state.set_num,
            "epoints": st.session_state.tlocations
        }
        st.session_state.results.append(result)

        # Move to the next actor or to the results page
        if st.session_state.current_actor_index < st.session_state.selected_actor_count:
            st.session_state.current_actor_index += 1
            st.session_state.selected_region = []  # Reset selected regions for next actor
            st.session_state.selected_angle = None  # Reset selected angle for next actor
            st.session_state.page = PAGES["Second Page"]
        else:
            st.session_state.page = PAGES["Fourth Page"]

def fourth_page():
    st.set_option('deprecation.showPyplotGlobalUse', False)
    st.title("Your Results")
    st.write(f"{st.session_state.results}")

#d['key4']
    act1 = st.session_state.results[0]
    actnums = act1['actor']
    region1 = act1['regions']
    set1 = act1['setpoint']
    points1 = act1['epoints'] 

    if len(st.session_state.results) > 1:
        act2 = st.session_state.results[1]
        actnums = act2['actor']
        region2 = act2['regions']
        points2 = act2['epoints'] 
        set2 = act2['setpoint']

        if len(st.session_state.results) > 2:
            act3= st.session_state.results[2]
            actnums = act3['actor']
            region3 = act3['regions']
            points3 = act3['epoints'] 
            set3 = act3['setpoint']

    


    if actnums == 3: 
        P = t.setup_actor3(region1, set1, points1, region2, set2, points2, region3, set3, points3)
    elif actnums == 2: 
        P = t.setup_actor2(region1, set1, points1, region2, set2, points2)
    else:
        P = t.setup_actor1(region1, set1, points1)
    st.write(P)


    # points = st.session_state.tlocations


    #st.title(f"Fip: {fig}")

    # Display the plot using Streamlit
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





    # st.title(f"Emipoints: {t.emipoints}")


if __name__ == "__main__":
    main()
