import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt

st.set_page_config(layout='wide', page_title='Restaurant Review Analysis')
st.header('Restaurant Review Analysis')
st.subheader('KAVUCIKA P')  

@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/skathirmani/datasets/refs/heads/main/restaurant_reviews.csv"
    reviews=pd.read_csv(url)
    reviews['rating'] = reviews['rating'].str.extract(r'(\d+)').astype(float)
    reviews['date'] = pd.to_datetime(reviews['date'], format='%d/%m/%y %H:%M', errors='coerce')
    reviews['Monthname'] = reviews['date'].dt.strftime('%B')
    rev_counts = reviews['rev_count'].str.split(' ', n=2, expand=True)
    rev_counts.columns = ['reviews_count', 'followers_count', 'extra']
    rev_counts['reviews_count'] = pd.to_numeric(rev_counts['reviews_count'], errors='coerce').fillna(0).astype(int)
    rev_counts['followers_count'] = pd.to_numeric(rev_counts['followers_count'], errors='coerce').fillna(0).astype(int)
    reviews[['reviews_count', 'followers_count']] = rev_counts[['reviews_count', 'followers_count']]
    return reviews

data = load_data()

st.write("Columns in the dataset:", data.columns.tolist())

st.write("Here is the restaurant reviews data:")
st.dataframe(data)

st.sidebar.header("Filters")

search_text = st.sidebar.text_input("Search reviews (by text):")
if search_text:
    data = data[data['text'].str.contains(search_text, case=False, na=False)]

months = data['Monthname'].dropna().unique()
selected_month = st.sidebar.selectbox("Filter by Month:", ['All'] + months.tolist())
if selected_month != 'All':
    data = data[data['Monthname'] == selected_month]

min_rating, max_rating = st.sidebar.slider("Filter by Rating", 0.0, 5.0, (0.0, 5.0), step=0.5)
data = data[(data['rating'] >= min_rating) & (data['rating'] <= max_rating)]

if data['reviews_count'].nunique() > 1:
    min_reviews, max_reviews = st.sidebar.slider(
        "Filter by Number of Reviews (Users)",
        int(data['reviews_count'].min()),
        int(data['reviews_count'].max()),
        (int(data['reviews_count'].min()), int(data['reviews_count'].max()))
    )
else:
    min_reviews, max_reviews = 0, int(data['reviews_count'].max())

data = data[(data['reviews_count'] >= min_reviews) & (data['reviews_count'] <= max_reviews)]

if data['followers_count'].nunique() > 1:
    min_followers, max_followers = st.sidebar.slider(
        "Filter by Followers Count (Users)",
        int(data['followers_count'].min()),
        int(data['followers_count'].max()),
        (int(data['followers_count'].min()), int(data['followers_count'].max()))
    )
else:
    min_followers, max_followers = 0, int(data['followers_count'].max())

data = data[(data['followers_count'] >= min_followers) & (data['followers_count'] <= max_followers)]

if 'res_name' in data.columns:
    top_restaurants = (data.groupby('res_name')['rating'].mean().nlargest(5).reset_index())
    if not top_restaurants.empty:
        fig_restaurants = px.bar(top_restaurants, 
                                  x='res_name', 
                                  y='rating', 
                                  title='Top 5 Restaurants Based on Average Rating',
                                  labels={'res_name': 'Restaurant Name', 'rating': 'Average Rating'},
                                 )
        st.plotly_chart(fig_restaurants)
    else:
        st.write("No data available for the selected filters for restaurants.")

st.subheader("Monthly Review Distribution")
monthly_reviews = data.groupby('Monthname').size().reset_index(name='Review Count')
if not monthly_reviews.empty:
    fig_monthly = px.bar(monthly_reviews, x='Monthname', y='Review Count', 
                         title='Monthly Review Distribution', color='Review Count', 
                         color_continuous_scale='Plasma')
    st.plotly_chart(fig_monthly)
else:
    st.write("No data available for the selected filters for monthly distribution.")

st.subheader("Distribution of Reviews by Rating (Pie Chart)")
rating_counts = data['rating'].value_counts().reset_index(name='count')
rating_counts.columns = ['rating', 'count']
if not rating_counts.empty:
    fig_pie = px.pie(rating_counts, names='rating', values='count', 
                     title="Review Distribution by Rating", color='rating', 
                     color_discrete_sequence=px.colors.qualitative.Set3)
    st.plotly_chart(fig_pie)
else:
    st.write("No data available for the selected filters for review distribution by rating.")

st.subheader("Followers vs Reviews Count (Colored by Rating)")
if 'followers_count' in data.columns and 'reviews_count' in data.columns:
    fig_scatter = px.scatter(data, x="followers_count", y="reviews_count", color="rating", 
                             title="Followers vs Reviews Count (Colored by Rating)",
                             labels={'followers_count': 'Followers Count', 'reviews_count': 'Reviews Count'},
                             color_continuous_scale='Viridis')
    st.plotly_chart(fig_scatter)
else:
    st.write("Necessary columns for the scatter plot are missing.")

st.subheader("Average Rating Over Time (Line Graph)")
if 'date' in data.columns:
    avg_rating_over_time = data.groupby(data['date'].dt.date)['rating'].mean().reset_index()
    if not avg_rating_over_time.empty:
        fig_line = px.line(avg_rating_over_time, x='date', y='rating', 
                           title="Average Rating Over Time", 
                           labels={'date': 'Date', 'rating': 'Average Rating'},
                           line_shape='linear')
        st.plotly_chart(fig_line)
    else:
        st.write("No data available for the average rating over time.")

st.write("Filtered Reviews:")
st.dataframe(data)

