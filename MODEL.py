import joblib
import pandas as pd
import numpy as np

import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer as wnl
from nltk.tokenize import word_tokenize
# from sklearn.feature_extraction.text import  TfidfVectorizer
# from sklearn.ensemble import RandomForestClassifier
import emoji
import re

# nltk.download('stopwords')
# nltk.download('wordnet')
# nltk.download('punkt')
# nltk.download('punkt_tab')
# english_stopwords = set(stopwords.words('russian'))
#
# model = joblib.load('C:/Users/Kanat/OneDrive/Рабочий стол/unik/MoodReviews/gb_model.pkl')
# vectorizer = joblib.load('C:/Users/Kanat/OneDrive/Рабочий стол/unik/MoodReviews/tfidf_vectorizer.pkl')
#
# emoji_pattern = r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F700-\U0001F77F\U0001F780-\U0001F7FF\U0001F800-\U0001F8FF\U0001F900-\U0001F9FF\U0001FA00-\U0001FA6F\U0001FB00-\U0001FBFF]'
# pattern = r'[^\w\s!?' + emoji_pattern + r']'

def text_preprocess(text, pattern, english_stopwords):
  text = text.lower()

  text = re.sub(pattern, ' ', text)
  text = ' '.join(text.split())

  tokens = word_tokenize(text)
  words = [wnl().lemmatize(word=i) for i in tokens if i not in english_stopwords]

  text = ' '.join(words)
  return text

def text_future_preprocess(data, tokenizator):
  tokens = tokenizator.transform(data)
  return tokens

def preprocess(X, vectorizer, pattern, english_stopwords):
  X['text'] = X['text'].apply(lambda x: text_preprocess(x, pattern, english_stopwords))
  X_text = text_future_preprocess(X['text'], vectorizer)
  X_text_df = pd.DataFrame(X_text.toarray(), index= None)

  X.reset_index(drop=True, inplace=True)
  X_text_df.reset_index(drop=True, inplace=True)
  X_text_df.columns = X_text_df.columns.astype(str)

  X_tfidf_train = pd.concat([X_text_df, X['stars']], axis=1)
  X_tfidf_train = X_tfidf_train.apply(lambda col: pd.to_numeric(col, errors='coerce') if col.dtype == 'object' else col)

  return X_tfidf_train


def result_analyze(pred_df):
  all_reviews_count = len(pred_df)
  possitive_reviews_count = len(pred_df[pred_df['mood'] == 2]) / all_reviews_count * 100
  neutral_reviews_count = len(pred_df[pred_df['mood'] == 1]) / all_reviews_count * 100
  neggative_reviews_count = len(pred_df[pred_df['mood'] == 0]) / all_reviews_count * 100

  result_text = f"Процент положительно настроенных отзывов: {possitive_reviews_count:.2f}%\n" \
                f"Процент нейтрально настроенных отзывов: {neutral_reviews_count:.2f}%\n" \
                f"Процент негативно настроенных отзывов: {neggative_reviews_count:.2f}%\n"

  return result_text, possitive_reviews_count, neutral_reviews_count, neggative_reviews_count

def analyze_reviews(reviews, vectorizer, model, pattern, english_stopwords):
  df_reviews = pd.DataFrame(reviews, index=None)
  df_reviews.dropna(inplace=True)

  X = df_reviews.drop(['id'], axis=1)
  X = preprocess(X, vectorizer, pattern, english_stopwords)

  pred = model.predict(X)
  pred_df = pd.DataFrame(pred, columns=['mood'])
  print(pred_df['mood'].unique())

  result_mess, positive_reviews_count, neutral_reviews_count, negative_reviews_count = result_analyze(pred_df)
  return result_mess, positive_reviews_count, neutral_reviews_count, negative_reviews_count