import pandas as pd
import streamlit as st
import plotly.express as px

#name of the web page
st.set_page_config(layout='wide', page_title='Restaurant Review Analysis')

# 1.Write a header "Restaurant Review Analysis". Make sure to add your name below it

st.header('Restaurant Review Analysis')
st.subheader('KAVUCIKA P')  

# 2.Read the data from following url. And make sure to cache it in streamlit app 
# url: https://raw.githubusercontent.com/skathirmani/datasets/refs/heads/main/restaurant_reviews.csv

@st.cache_data
def load_data():
  url = 'https://raw.githubusercontent.com/skathirmani/datasets/refs/heads/main/restaurant_reviews.csv'
  reviews = pd.read_csv(url)

  #doing this step to ensure that the column names we give is correctly matched with the column name in the data frame
  st.write("Column names in the DataFrame:", reviews.columns)

  # 3.Clean the `rating` column to extract only the rating as number
  ##reviews['rating_cleaned']=reviews['rating'].str.replace('Rated','').astype(float).astype(int)

  reviews['rating'] = reviews['rating'].str.extract('(\d+\.\d+|\d+)')[0].astype(float)  
  reviews['date'] = pd.to_datetime(reviews['date'], format='%d/%m/%y %H:%M')  
  reviews['Monthname'] = reviews['date'].dt.month_name() 
  return reviews

reviews = load_data()

# displaying the dataframe to see what are in the given url
st.write("Here is the restaurant reviews data:")
st.dataframe(reviews)

# 4.Use `st.sidebar.text_input` to filter rows based on words in `text` column.
text_filter = st.sidebar.text_input('Search text in reviews')

# 5.Extract `Monthname` from `date` column, and create a `Monthname` filter (selectbox/dropdown)
#  - Hint: `reviews['date'] = pd.to_datetime(reviews['date'], format='%d/%m/%y %H:%M')`

#`reviews['date'] = pd.to_datetime(reviews['date'], format='%d/%m/%y %H:%M')`
#reviews['Monthname']=reviews['date'].dt.strftime('%B')
month_filter = st.sidebar.selectbox(
    label="Select a Month",
    options=reviews['Monthname'].unique(),
    index=0  
)

# applying filters to replicate on graphs
filtered_reviews = reviews[
    (reviews['text'].str.contains(text_filter, na=False)) &   
    (reviews['Monthname'] == month_filter)                     
]

# 6.Create a bar chart, to visualize Top 5 Restaurants based on average `rating`
top_restaurants = (filtered_reviews.groupby('res_name')['rating']
                   .mean()
                   .sort_values(ascending=False)
                   .head(5)
                   .reset_index())

fig_restaurants = px.bar(
    top_restaurants,
    x='res_name',
    y='rating',   
    title="Top 5 Restaurants by Average Rating",
    labels={'res_name': 'Restaurant', 'rating': 'Average Rating'}
)

st.plotly_chart(fig_restaurants)

# 7.Using `rev_count` create two new columns, one for `reviews_count` and another for `followers_count`. 
#reviews['rev_count'].str.split(',').str[0].str.replace(' Reviews','')...........>concept to do
#reviews['rev_count'].str.split(',').str[0].str.replace(' Reviews','').astype(float)
#

filtered_reviews[['reviews_count', 'followers_count']] = filtered_reviews['rev_count'].str.extract('(\d+)\s*reviews,\s*(\d+)\s*followers')

# conerting missing values by Fill missing values (NaN) with 0, then convert to integers
filtered_reviews['reviews_count'] = filtered_reviews['reviews_count'].fillna(0).astype(int)
filtered_reviews['followers_count'] = filtered_reviews['followers_count'].fillna(0).astype(int)

st.write("Updated DataFrame with 'reviews_count' and 'followers_count':")
st.dataframe(filtered_reviews)

# 8.Create a bar chart, to visualize Top 5 Users based on total `followers_count`
top_users = (filtered_reviews.groupby('rev_name')['followers_count']
             .sum()
             .sort_values(ascending=False)
             .head(5)
             .reset_index())

fig_users = px.bar(
    top_users,
    x='rev_name',  
    y='followers_count',
    title="Top 5 Users by Followers Count"
)
st.plotly_chart(fig_users)

# 9.Display the filtered dataframe below the charts
st.write("Filtered reviews based on your selection:")
st.dataframe(filtered_reviews)