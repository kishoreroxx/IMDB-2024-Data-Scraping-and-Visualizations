import streamlit as st
import pandas as pd
import mysql.connector
import plotly.express as px
import matplotlib.pyplot as plt

# ---------------------- Database Connection ----------------------
connection = mysql.connector.connect(
    host="gateway01.ap-southeast-1.prod.aws.tidbcloud.com",
    port=4000,
    user="2xvdoy7zCoXHMqP.root",
    password="UYKqDha1tVD4QkMY",
    database="test",
)
mycursor = connection.cursor(buffered=True)
mycursor.execute("SELECT * FROM Project_1.Project_1")
data = mycursor.fetchall()
df = pd.DataFrame(data, columns=mycursor.column_names)

# Pre-clean data
df = df[df['duration_minutes'].notnull() & df['ratings'].notnull() & df['voting'].notnull()]
df['duration_hours'] = df['duration_minutes'] / 60

# ---------------------- Top Radio Selector ----------------------
st.sidebar.title("Navigation")
view_option = st.sidebar.radio("Choose View Mode", ["Data Visualization", "Interactive Data Visualization"])

# ---------------------- INTERACTIVE DATA VISUALIZATION ----------------------
if view_option == "Interactive Data Visualization":
    st.title("🎬 Movie Explorer with Interactive Filters")

    # Sidebar Filters
    st.sidebar.header("🔍 Filter Your Movies")

    # Duration Filter
    duration_filter = st.sidebar.radio("Duration (Hrs)", ['All', '< 2 hrs', '2-3 hrs', '> 3 hrs'])
    if duration_filter == '< 2 hrs':
        df = df[df['duration_hours'] < 2]
    elif duration_filter == '2-3 hrs':
        df = df[(df['duration_hours'] >= 2) & (df['duration_hours'] <= 3)]
    elif duration_filter == '> 3 hrs':
        df = df[df['duration_hours'] > 3]

    # Rating Filter
    min_rating = st.sidebar.slider("Minimum Rating", min_value=0.0, max_value=10.0, value=0.0, step=0.5)
    df = df[df['ratings'] >= min_rating]

    # Votes Filter
    min_votes = st.sidebar.number_input("Minimum Votes", min_value=0, value=0, step=1000)
    df = df[df['voting'] >= min_votes]

    # Genre Filter
    genres = df['genre'].dropna().unique().tolist()
    selected_genres = st.sidebar.multiselect("Select Genres", options=genres, default=genres)
    df = df[df['genre'].isin(selected_genres)]

    # Display Filtered Results
    st.subheader("🎯 Filtered Movie Results")
    st.write(f"**{len(df)} movies** match your criteria.")
    st.dataframe(df[['movie_name', 'genre', 'ratings', 'voting', 'duration_minutes']].sort_values(by='ratings', ascending=False))

# ---------------------- DATA VISUALIZATION ----------------------
elif view_option == "Data Visualization":
    st.title("📊 Movie Data Visualizations")

    question = st.selectbox("Select a Visualization Question", [
        "Question 1 - Top 10 Movies by Rating and Voting",
        "Question 2 - Genre Distribution",
        "Question 3 - Average Duration per Genre",
        "Question 4 - Average Voting per Genre",
        "Question 5 - Distribution of Ratings",
        "Question 6 - Top Rated Movie per Genre",
        "Question 7 - Total Votes by Genre (Pie Chart)",
        "Question 8 - Shortest and Longest Movies",
        "Question 9 - Heatmap of Avg Ratings by Genre",
        "Question 10 - Scatter Plot: Ratings vs Voting"
    ])

    if question == "Question 1 - Top 10 Movies by Rating and Voting":
        top_movies = df.sort_values(['ratings', 'voting'], ascending=[False, False]).head(10)

        fig_rating = px.bar(top_movies, x='movie_name', y='ratings', title='Top 10 Movies by Rating',
                            labels={'movie_name': 'Movie Title', 'ratings': 'Rating'})
        fig_rating.update_layout(yaxis=dict(tickmode='linear', dtick=0.5, range=[1, 10]))
        st.plotly_chart(fig_rating)

        fig_votes = px.bar(top_movies, x='movie_name', y='voting', title='Top 10 Movies by Voting Count',
                           labels={'movie_name': 'Movie Title', 'voting': 'Number of Votes'})
        st.plotly_chart(fig_votes)

    elif question == "Question 2 - Genre Distribution":
        genre_counts = df.groupby('genre')['movie_name'].count()
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.bar(genre_counts.index, genre_counts.values)
        ax.set_xlabel('Genre')
        ax.set_ylabel('Number of Movies')
        ax.set_title('Genre Distribution')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        st.pyplot(fig)

    elif question == "Question 3 - Average Duration per Genre":
        avg_duration = df.groupby('genre')['duration_minutes'].mean().reset_index()
        fig_duration = px.bar(avg_duration, x='duration_minutes', y='genre', orientation='h',
                              title='Average Movie Duration per Genre')
        fig_duration.update_layout(xaxis=dict(range=[80, 110]), yaxis=dict(categoryorder='total ascending'))
        st.plotly_chart(fig_duration)

    elif question == "Question 4 - Average Voting per Genre":
        avg_votes = df.groupby('genre')['voting'].mean().reset_index()
        fig = px.bar(avg_votes, x='voting', y='genre', orientation='h',
                     title='Average Voting Counts Across Genres', color='voting',
                     color_continuous_scale='Blues')
        fig.update_layout(yaxis=dict(categoryorder='total ascending'))
        fig.update_traces(texttemplate='%{x:.0f}', textposition='outside')
        st.plotly_chart(fig)

    elif question == "Question 5 - Distribution of Ratings":
        fig_rating_hist = px.histogram(df, x='ratings', nbins=20,
                                       title='Distribution of Movie Ratings',
                                       color_discrete_sequence=['indigo'])
        fig_rating_hist.update_layout(bargap=0.1, xaxis=dict(dtick=0.5), yaxis_title='Count')
        st.plotly_chart(fig_rating_hist)

    elif question == "Question 6 - Top Rated Movie per Genre":
        top_rated_per_genre = df.sort_values(['genre', 'ratings'], ascending=[True, False])
        top_rated_per_genre = top_rated_per_genre.groupby('genre').first().reset_index()
        st.subheader("🎬 Top-Rated Movie by Genre")
        st.dataframe(top_rated_per_genre[['genre', 'movie_name', 'ratings', 'voting', 'duration_minutes']].sort_values('ratings', ascending=False))

    elif question == "Question 7 - Total Votes by Genre (Pie Chart)":
        votes_by_genre = df.groupby('genre')['voting'].sum().reset_index().sort_values(by='voting', ascending=False)
        fig = px.pie(votes_by_genre, values='voting', names='genre', title='Total Voting Counts by Genre',
                     hole=0.4, color_discrete_sequence=px.colors.sequential.RdBu)
        fig.update_traces(textinfo='percent+label', pull=[0.05]*len(votes_by_genre))
        st.plotly_chart(fig)

    elif question == "Question 8 - Shortest and Longest Movies":
        # Remove invalid or missing durations
        df = df[df['duration_minutes'].notnull() & (df['duration_minutes'] > 0)]
        shortest_movie = df.loc[df['duration_minutes'].idxmin()]
        longest_movie = df.loc[df['duration_minutes'].idxmax()]
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 🎬 Shortest Movie")
            st.markdown(f"""
                <div style='border:1px solid #ccc; border-radius:10px; padding:20px; background-color:#fff8dc; color: #333; box-shadow: 2px 2px 10px rgba(0,0,0,0.05);'>
                    <h4>{shortest_movie['movie_name']}</h4>
                    <p><strong>Genre:</strong> {shortest_movie['genre']}</p>
                    <p><strong>Duration:</strong> {shortest_movie['duration_minutes']} minutes</p>
                    <p><strong>Rating:</strong> {shortest_movie['ratings']}</p>
                </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown("### 🎬 Longest Movie")
            st.markdown(f"""
                <div style='border:1px solid #ccc; border-radius:10px; padding:20px; background-color:#fff8dc; color: #333; box-shadow: 2px 2px 10px rgba(0,0,0,0.05);'>
                    <h4>{longest_movie['movie_name']}</h4>
                    <p><strong>Genre:</strong> {longest_movie['genre']}</p>
                    <p><strong>Duration:</strong> {longest_movie['duration_minutes']} minutes</p>
                    <p><strong>Rating:</strong> {longest_movie['ratings']}</p>
                </div>
            """, unsafe_allow_html=True)

    elif question == "Question 9 - Heatmap of Avg Ratings by Genre":
        avg_ratings = df.groupby('genre')['ratings'].mean().reset_index()
        avg_ratings['dummy'] = 'Average Rating'
        fig = px.density_heatmap(avg_ratings, x='genre', y='dummy', z='ratings',
                                 color_continuous_scale='YlGnBu', title='🔥 Heatmap of Average Ratings by Genre')
        fig.update_layout(yaxis_title="", xaxis_title="Genre", height=400)
        st.plotly_chart(fig)

    elif question == "Question 10 - Scatter Plot: Ratings vs Voting":
        filtered_df = df[df['voting'] < df['voting'].quantile(0.99)]
        fig = px.scatter(filtered_df, x='ratings', y='voting', hover_data=['movie_name', 'genre'],
                         color='genre', size='voting', title='🎯 Relationship Between Movie Ratings and Voting Counts')
        st.plotly_chart(fig)