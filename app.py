import streamlit as st
import pandas as pd
import altair as alt
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px


# Configure Streamlit App
st.set_page_config(page_title="Shark Attack Dashboard", layout="wide")

# Navigation Bar with Icons (using emojis for simplicity)
page = st.sidebar.radio(
    "Select a Page:",
    options=["Home Page", "Shark Species", "Victim Demographics"],
    index=0  # Default starting page
)

# Load the CSV File
file_path = "filtered_file.csv"
try:
    data = pd.read_csv(file_path, on_bad_lines="skip")
except Exception as e:
    st.error(f"Error loading file: {e}")
    st.stop()

# Preprocess Data
data["Year"] = pd.to_numeric(data.get("Year", None), errors="coerce")
data_cleaned = data.dropna(subset=["Year"])
data_cleaned["Year"] = data_cleaned["Year"].astype(int)
data_cleaned = data_cleaned[(data_cleaned["Year"] >= 2014) & (data_cleaned["Year"] <= 2023)]

# Dropdown filter for the Home Page
if page == "Home Page":
    st.markdown(
        """
        <h1 style="text-align: center; margin-top: 0%;">Shark Attack Analysis (2014-2023)</h1>
        """,
    unsafe_allow_html=True
)    
    st.markdown(
        """
        ---
        Welcome to the **Shark Attack Streamlit App**!  
        This app provides insights into global shark attack trends from 2014-2023.  
        Explore patterns in attack locations, types, and severity, helping to enhance safety awareness in ocean activities.
        """
    )

    # Dropdown filter for year
    years = sorted(data_cleaned["Year"].unique())
    selected_year = st.selectbox(
        "Select a Year for Analysis", 
        options=["All"] + years
    )

    if selected_year == "All":
        filtered_data = data_cleaned
    else:
        filtered_data = data_cleaned[data_cleaned["Year"] == selected_year]

    if filtered_data.empty:
        st.warning("No data available for the selected year!")
    else:
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### Shark Attacks Over Time")
            yearly_counts = filtered_data.groupby("Year").size()
            if not yearly_counts.empty:
                fig, ax = plt.subplots(figsize=(8, 6))
                sns.set(style="whitegrid")
                sns.lineplot(x=yearly_counts.index, y=yearly_counts.values, marker="o", ax=ax, color="#1f77b4", lw=4)
                ax.set_title("Global Shark Attacks Over the Years", fontsize=16, fontweight="bold", color="darkblue")
                ax.set_xlabel("Year", fontsize=14)
                ax.set_ylabel("Number of Attacks", fontsize=14)
                ax.tick_params(axis="both", labelsize=12)
                ax.grid(True, linestyle="--", alpha=0.7)
                st.pyplot(fig)

        with col2:
            st.markdown("### Average Age by Attack Type")
            age_data = filtered_data.copy()
            attack_types_to_include = ['Watercraft', 'Sea Disaster', 'Provoked', 'Unprovoked']
            age_data = age_data[age_data['Type'].isin(attack_types_to_include)]
            age_data["Age"] = pd.to_numeric(age_data["Age"], errors="coerce")
            avg_age_by_attack_type = age_data.groupby("Type")["Age"].mean().reset_index()

            if not avg_age_by_attack_type.empty:
                bar_chart = alt.Chart(avg_age_by_attack_type).mark_bar(size=30).encode(
                    x=alt.X("Age:Q", title="Average Age"),
                    y=alt.Y("Type:N", title="Attack Type", sort="-x"),
                    color=alt.Color("Type:N", legend=None)
                ).properties(
                    width=400,
                    height=300
                )
                st.altair_chart(bar_chart, use_container_width=True)

    st.markdown(
        """
        ---
        **Also Important to Know**  
        Warmer waters and popular beaches see more attacks, especially during the summer months when more people are swimming or surfing. Understanding these factors can help predict and mitigate future risks.
        """
    )

# More Data Page      
elif page == "Shark Species":
    st.markdown(
        """
        <h1 style="text-align: center; margin-top: 0%;">Taking a Closer Look at Shark Species Attacking</h1>
        """,
    unsafe_allow_html=True
)    
    st.markdown("Species Involvement in Fatal Attacks")

    st.markdown(
    """
    Larger, more aggressive species like the Great White and Tiger sharks are linked to higher fatality rates. 
    Understanding which species pose the greatest risk can guide safety measures and conservation efforts.
    """
)

    # Dropdown filter for year (same as on Home Page)
    years = sorted(data_cleaned["Year"].unique())
    selected_year = st.selectbox(
        "Select a Year for Analysis", 
        options=["All"] + years
    )

    # Load and preprocess data
    data.columns = data.columns.str.strip()
    data.columns = data.columns.str.lower()

    # Ensure 'year' is numeric
    data['year'] = pd.to_numeric(data.get('year', None), errors='coerce')

    # Filter years 2014-2023 and drop rows with missing values in essential columns
    data = data.dropna(subset=['year'])
    data = data[data['year'].between(2014, 2023)]

    # Check for required columns
    required_columns = ['species', 'year']
    if not all(col in data.columns for col in required_columns):
        st.error(f"The required columns {required_columns} are missing in the dataset.")
        st.stop()

    # Filter for specific shark species
    species_of_interest = ['White shark', 'Bull shark', 'Tiger shark', 'Mako shark', 'Grey reef']
    filtered_data = data[data['species'].str.lower().isin([s.lower() for s in species_of_interest])]

    # Group data by Species and count occurrences
    bar_chart_data = filtered_data.groupby(['species']).size().reset_index(name='count')

    # Create a bar chart using Altair
    st.markdown("### Shark Attacks by Species")
    chart = alt.Chart(bar_chart_data).mark_bar().encode(
        x=alt.X('species:N', title='Species', sort=species_of_interest),
        y=alt.Y('count:Q', title='Count of Shark Attacks'),
        color=alt.Color('species:N', title='Species')
    ).properties(
        width=600,  # Chart width
        height=400  # Chart height
    )

    # Display the chart
    st.altair_chart(chart, use_container_width=True)

    # Pie Chart Start
    data['year'] = pd.to_numeric(data['year'], errors='coerce')
    data = data.dropna(subset=['year'])
    data = data[data['year'].between(2013, 2023)]

    # Ensure 'Age' is numeric and drop missing values
    data['age'] = pd.to_numeric(data['age'], errors='coerce')
    data = data.dropna(subset=['age', 'sex'])

    # Calculate average age by sex
    demographics = data.groupby('sex')['age'].mean().reset_index()
    demographics.columns = ['Sex', 'Average Age']


elif page == "Victim Demographics":

    st.markdown(
        """
        <h1 style="text-align: center; margin-top: 0%;">Victim Demographics</h1>
        """,
    unsafe_allow_html=True
)      
    st.markdown("Who is getting attacked?")

    st.markdown("""
    It's important to know what time of day, what species, and understand what demographics are affected most by these attacks. 
    This information can help enhance safety measures and inform high-risk situations.
    """)

    # Dropdown filter for year (same as on Home Page)
    years = sorted(data_cleaned["Year"].unique())
    selected_year = st.selectbox(
        "Select a Year for Analysis", 
        options=["All"] + years
    )

    # Load and preprocess data
    data.columns = data.columns.str.strip()
    data.columns = data.columns.str.lower()

    # Ensure 'year' is numeric and filter for years 2013–2023
    data['year'] = pd.to_numeric(data['year'], errors='coerce')
    data = data.dropna(subset=['year'])
    data = data[data['year'].between(2013, 2023)]

    # Ensure 'Age' is numeric and drop missing values
    data['age'] = pd.to_numeric(data['age'], errors='coerce')
    data = data.dropna(subset=['age', 'sex'])

    # --- Pie Chart: Average Age by Sex ---
    demographics = data.groupby('sex')['age'].mean().reset_index()
    demographics.columns = ['Sex', 'Average Age']
    fig_pie = px.pie(
        demographics,
        values='Average Age',
        names='Sex',
        title="Victim Demographics: Average Age by Sex",
        color_discrete_sequence=px.colors.sequential.Blues_r
    )

    # --- Fatality by Sex and Average Age ---
    required_columns = ['sex', 'fatal (y/n)', 'age', 'year']
    if not all(col in data.columns for col in required_columns):
        st.error(f"The required columns {required_columns} are missing in the dataset.")
        st.stop()

    data['fatal (y/n)'] = data['fatal (y/n)'].str.upper()
    data = data[data['fatal (y/n)'].isin(['Y', 'N'])]
    fatality_analysis = data.groupby(['sex', 'fatal (y/n)'])['age'].mean().reset_index()
    fatality_pivot = fatality_analysis.pivot_table(
        index='fatal (y/n)', 
        columns='sex', 
        values='age', 
        aggfunc='mean'
    )

    # --- Time of Shark Attacks ---
    if "time" in data.columns:
        data['hour'] = data['time'].str.extract(r'(\d+)h').astype(float)
        data = data.dropna(subset=['hour'])
    else:
        st.error("The required column 'time' is missing in the dataset.")
        st.stop()

    time_attack_analysis = data.groupby('hour')['name'].nunique().reset_index()
    time_attack_analysis.columns = ['Hour', 'Distinct Attack Count']

    # --- Layout with Columns ---
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Victim Demographics: Average Age by Sex")
        st.plotly_chart(fig_pie, use_container_width=True)

    with col2:
        st.markdown("### Fatality by Sex and Average Age")
        st.dataframe(
            fatality_pivot.style.background_gradient(cmap="Blues", axis=None),
            use_container_width=True
        )

    st.markdown("### Time of Shark Attacks (Hour of Day)")
    st.write(time_attack_analysis.style.background_gradient(cmap='Blues', subset=['Distinct Attack Count']))
