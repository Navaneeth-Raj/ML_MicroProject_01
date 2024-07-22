import streamlit as st
import pandas as pd
import numpy as np
import base64

def format_input(movies, ratings):
  """
  Formats user input with comma-separated entries into a list of dictionaries.

  Args:
      movies (str): User input containing comma-separated movie titles.
      ratings (str): User input containing comma-separated ratings.

  Returns:
      list: A list of dictionaries containing movie titles and ratings.
  """

  # Split movie and rating strings into separate lists
  movie_list = movies.strip().splitlines()
  rating_list = ratings.strip().splitlines()

  # Check if movie and rating lists have the same length
  if len(movie_list) != len(rating_list):
      st.error("Please ensure you enter the same number of movies and ratings.")
      return None  

  data = []
  for i, movie_str in enumerate(movie_list):
      try:
          # Split movies at commas and strip leading/trailing spaces
          movies = [movie.strip() for movie in movie_str.split(",")]

          # Split ratings at commas and convert to floats
          ratings = [float(rating.strip()) for rating in rating_list[i].split(",")]

          if len(movies) != len(ratings):
              st.error(f"Invalid pair count in line {i+1}. Please ensure equal movie and rating entries.")
              return None  # Return None on mismatch

          # Add movie-rating pairs as dictionaries to the data list
          for movie, rating in zip(movies, ratings):
              data.append({'title': movie, 'rating': rating})

      except ValueError:
          st.error(f"Invalid format in line {i+1}. Please use comma-separated movies and numbers for ratings.")
          return None  

  return data


st.title('Movie Genie || Movie Recommender')

ratings = pd.read_csv('ratings.csv')
movies = pd.read_csv('movies.csv')

movies['title'] = movies.title.str.replace(r'(\(\d{4}\))', '', regex=True)
movies['title'] = movies['title'].apply(lambda x: x.strip() if isinstance(x, str) else x)
movies = movies.drop('genres', axis= 1)

ratings = ratings.drop('timestamp', axis= 1)

with st.form('my_form'):
  usr_movie = st.text_area('Enter Some Movies : ',key='movie_key')
  usr_rating = st.text_area('Enter Corresponding Ratings : ',key='rating_key')
  button = st.form_submit_button('Submit Preferences')

if button:
  userInput = format_input(usr_movie,usr_rating)
  inputMovies = pd.DataFrame(userInput)
  inputId = movies[movies['title'].isin(inputMovies['title'].tolist())]
  inputMovies = pd.merge(inputId, inputMovies)

  userSubset = ratings[ratings['movieId'].isin(inputMovies['movieId'].tolist())]

  userSubsetGroup = userSubset.groupby(['userId'])
  userSubsetGroup = sorted(userSubsetGroup,  key=lambda x: len(x[1]), reverse=True)
  userSubsetGroup = userSubsetGroup[0:100]
  pearsonCorrelationDict = {}
  for name, group in userSubsetGroup:

      #Start by sorting the input and current user group so the values aren't mixed up later
      group = group.sort_values(by='movieId')
      inputMovies = inputMovies.sort_values(by='movieId')

      #Get the N (total similar movies watched) for the formula
      nRatings = len(group)

      #Get the review scores for the movies that they both have in common
      temp_df = inputMovies[inputMovies['movieId'].isin(group['movieId'].tolist())]

      #And then store them in a temporary buffer variable in a list format to facilitate future calculations
      tempRatingList = temp_df['rating'].tolist()

      #Let's also put the current user group reviews in a list format
      tempGroupList = group['rating'].tolist()

      Sxx = sum([i**2 for i in tempRatingList]) - pow(sum(tempRatingList),2)/float(nRatings)
      Syy = sum([i**2 for i in tempGroupList]) - pow(sum(tempGroupList),2)/float(nRatings)
      Sxy = sum( i*j for i, j in zip(tempRatingList, tempGroupList)) - sum(tempRatingList)*sum(tempGroupList)/float(nRatings)
      if Sxx != 0 and Syy != 0:
          pearsonCorrelationDict[name] = Sxy/np.sqrt(Sxx*Syy)
      else:
          pearsonCorrelationDict[name] = 0


  pearsonDF = pd.DataFrame.from_dict(pearsonCorrelationDict, orient='index')

  pearsonDF.columns = ['similarityIndex']
  pearsonDF['userId'] = pearsonDF.index
  pearsonDF.index = range(len(pearsonDF))
  topUsers=pearsonDF.sort_values(by='similarityIndex', ascending=False)[0:50]

  topUsersRating = pd.concat([topUsers, ratings], axis=1)

  topUsersRating['weightedRating'] = topUsersRating['similarityIndex']*topUsersRating['rating']

  tempTopUsersRating = topUsersRating.groupby('movieId').sum()[['similarityIndex','weightedRating']]
  tempTopUsersRating.columns = ['sum_similarityIndex','sum_weightedRating']

  recommendation_df = pd.DataFrame()
  recommendation_df['weighted average recommendation score'] = tempTopUsersRating['sum_weightedRating']/tempTopUsersRating['sum_similarityIndex']
  recommendation_df['movieId'] = tempTopUsersRating.index

  recommendation_df = recommendation_df.sort_values(by='weighted average recommendation score', ascending=False)

  output_df = movies.loc[movies['movieId'].isin(recommendation_df.head(20)['movieId'].tolist())]

  st.table(output_df) 




