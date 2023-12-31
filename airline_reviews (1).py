# -*- coding: utf-8 -*-
"""Airline_reviews.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1JLIO4us61x8TdIIYRAlBE5TRNGNFujUX
"""

import pandas as pd
import numpy as np

df= pd.read_csv('/content/Airline_review.csv')

df.info()

print("Null values count in each column before cleaning:\n",df.isnull().sum())

# Impute missing values for 'Aircraft' with a placeholder value, e.g., 'Unknown'
df['Aircraft'].fillna('Unknown', inplace=True)

# Impute missing values for categorical columns with the mode (most frequent value)
df['Type Of Traveller'].fillna(df['Type Of Traveller'].mode()[0], inplace=True)

# Impute missing values for 'Route' with a placeholder value, e.g., 'Unknown'
df['Route'].fillna('Unknown', inplace=True)

# Impute missing values for 'Date Flown' with a placeholder value, e.g., 'Unknown'
df['Date Flown'].fillna('Unknown', inplace=True)

# Impute missing values for numeric columns with the mean
numeric_columns = ['Seat Comfort', 'Cabin Staff Service', 'Food & Beverages', 'Ground Service', 'Inflight Entertainment', 'Wifi & Connectivity', 'Value For Money']
for column in numeric_columns:
    df[column].fillna(df[column].mean(), inplace=True)

# Verify that there are no more missing values
print("Null values count in each column after cleaning:\n",df.isnull().sum())

def map_n_rating(x):
    res = x
    if x == 'n':
        res = '1'

    return res

df["Overall_Rating"] = df["Overall_Rating"].apply(map_n_rating)

value_for_money_median_map = {
    "1": 1,
    "2": 1,
    "3": 2,
    "4": 2,
    "5": 3,
    "6": 4,
    "7": 4,
    "8": 4,
    "9": 5,
}

df['Median_value_for_money'] = df['Overall_Rating'].map(value_for_money_median_map)

df["Value For Money"] = df.apply(
    lambda row: row['Median_value_for_money'] if np.isnan(row["Value For Money"]) else row["Value For Money"],
    axis=1
)
df=df.drop(columns=['Median_value_for_money'])

df['Seat Type'] = df['Seat Type'].fillna('Economy Class')

df['Review Date'] = pd.to_datetime(df['Review Date'])

df['Type Of Traveller'] = df['Type Of Traveller'].astype('category')
df['Seat Type'] = df['Seat Type'].astype('category')
df['Recommended'] = df['Recommended'].map({'yes': 1, 'no': 0})

from google.colab import files

df.to_csv('Cleaned_df.csv')
files.download('Cleaned_df.csv')

import matplotlib.pyplot as plt
import seaborn as sns
from google.colab import files

from wordcloud import WordCloud

reviews_text = ' '.join(df['Review'].astype(str))
wordcloud = WordCloud(width=640, height=480, background_color='white').generate(reviews_text)
plt.figure(figsize=(12, 6))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')
plt.title('Word Cloud: Reviews')
plt.show()

recommended_counts = df['Recommended'].value_counts()
plt.figure(figsize=(8, 8))
plt.pie(recommended_counts, labels=recommended_counts.index, autopct='%1.1f%%', startangle=90, colors=['lightcoral', 'lightgreen'])
plt.gca().add_artist(plt.Circle((0,0),0.70,fc='white'))
plt.title('Donut Plot: Recommended Percentage')
plt.show()

rating_categories = ['Seat Comfort', 'Cabin Staff Service', 'Food & Beverages', 'Ground Service', 'Inflight Entertainment', 'Wifi & Connectivity', 'Value For Money']
ratings_means = df[rating_categories].mean()
angles = [n / float(len(rating_categories)) * 2 * 3.14159 for n in range(len(rating_categories))]
plt.figure(figsize=(6, 8))
plt.polar(angles, ratings_means, marker='o', linestyle='-', color='orange', linewidth=2, alpha=0.7)
plt.fill(angles, ratings_means, color='orange', alpha=0.25)
plt.title('Radar Chart: Average Ratings in Different Categories')
plt.xticks(angles, rating_categories)
plt.show()

plt.figure(figsize=(8, 8))
df['Recommended'].value_counts().plot.pie(autopct='%1.1f%%', colors=['skyblue', 'lightcoral'])
plt.title('Percentage of Recommended Airlines')
plt.show()

top_airlines_overall = df.groupby('Airline Name')['Overall_Rating'].mean().sort_values(ascending=False).head(10)

plt.figure(figsize=(12, 8))
sns.barplot(x=top_airlines_overall.values, y=top_airlines_overall.index, palette='viridis')
plt.title('Top 10 Airlines by Overall Ratings')
plt.xlabel('Overall Rating')
plt.show()

top_airlines_seat_comfort = df.groupby('Airline Name')['Seat Comfort'].mean().sort_values(ascending=False).head(10)

plt.figure(figsize=(8, 6))
sns.barplot(x=top_airlines_seat_comfort.values, y=top_airlines_seat_comfort.index, palette='plasma')
plt.title('Top 10 Airlines by Seat Comfort')
plt.xlabel('Seat Comfort Rating')
plt.show()

top_recommended_airlines = df[df['Recommended'] == 'yes']['Airline Name'].value_counts().head(5)

plt.figure(figsize=(8, 6))
sns.barplot(x=top_recommended_airlines.values, y=top_recommended_airlines.index, palette='pastel')
plt.title('Top 5 Airlines with Highest Recommendations')
plt.xlabel('Number of Recommendations')
plt.show()

df['Type Of Traveller'].info()

plt.figure(figsize=(8, 6))
sns.countplot(x='Type Of Traveller', data=df, palette='viridis')
plt.title('Distribution of Type of Traveller')
plt.xlabel('Type of Traveller')
plt.ylabel('Count')
plt.xticks(rotation=45, ha='right')
plt.show()

filtered_airlines = df.groupby('Airline Name').filter(lambda x: len(x) >= 50)

# Get the bottom 10 airlines based on average 'Value For Money' rating
bottom_10_airlines = filtered_airlines.groupby('Airline Name')['Value For Money'].mean().nsmallest(10)

# Plot
plt.figure(figsize=(8, 6))
sns.barplot(x=bottom_10_airlines.values, y=bottom_10_airlines.index, palette='viridis')
plt.title('Bottom 10 Airlines with Least Value For Money Rating (>=50 reviews)')
plt.xlabel('Average Value For Money Rating')
plt.ylabel('Airline Name')
plt.show()

from textblob import TextBlob

import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, LSTM, Dense

import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, WordNetLemmatizer

# Download NLTK resources
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('punkt')
# Initialize stemmer and lemmatizer
stemmer = PorterStemmer()
lemmatizer = WordNetLemmatizer()
def preprocess_text(text):
    # Convert to lowercase
    text = text.lower()
    words = nltk.word_tokenize(text)
    # Remove stop words
    words = [word for word in words if word not in stopwords.words('english')]
    # Apply stemming
    words = [stemmer.stem(word) for word in words]
    # Apply lemmatization
    words = [lemmatizer.lemmatize(word) for word in words]
    # Rejoin words to form processed text
    processed_text = ' '.join(words)
    return processed_text

# Apply text preprocessing to your dataset
df['Processed_Review'] = df['Review'].apply(preprocess_text)

df['Processed_Review']

df['Sentiment'] = df['Processed_Review'].apply(lambda x: 1 if TextBlob(str(x)).sentiment.polarity > 0 else 0)

positive_reviews = df[df['Sentiment'] > 0]
negative_reviews = df[df['Sentiment'] == 0]

# Count the number of reviews in each sentiment category
positive_count = positive_reviews.shape[0]
negative_count = negative_reviews.shape[0]

# Create a bar plot
plt.bar(['Positive', 'Negative'], [positive_count, negative_count], color=['blue', 'red'])
plt.xlabel('Sentiment')
plt.ylabel('Number of Reviews')
plt.title('Distribution of Sentiments in Reviews')
plt.show()

train_texts, test_texts, y_train, y_test = train_test_split(df['Processed_Review'], df['Sentiment'], test_size=0.2, random_state=42)

test_texts

y_test

tokenizer = Tokenizer(num_words=10000)  # You can adjust the vocabulary size
tokenizer.fit_on_texts(train_texts)

X_train = tokenizer.texts_to_sequences(train_texts)
X_test = tokenizer.texts_to_sequences(test_texts)

X_train = pad_sequences(X_train, maxlen=100)  # You can adjust the sequence length
X_test = pad_sequences(X_test, maxlen=100)

X_train

X_test

embedding_dim = 50  # You can adjust the embedding dimension
embedding_matrix = np.zeros((len(tokenizer.word_index) + 1, embedding_dim))

with open('/content/glove.6B.50d.txt', 'r', encoding='utf-8') as glove_file:
    for line in glove_file:
        values = line.split()
        word = values[0]
        if word in tokenizer.word_index:
            idx = tokenizer.word_index[word]
            embedding_matrix[idx] = np.array(values[1:], dtype='float32')

embedding_matrix

train_texts_list = train_texts.tolist()

from tensorflow.keras.layers import Conv1D, MaxPooling1D, Flatten

model_cnn = Sequential()
model_cnn.add(Embedding(len(tokenizer.word_index) + 1, embedding_dim, weights=[embedding_matrix], input_length=100, trainable=False))
model_cnn.add(Conv1D(128, 5, activation='relu'))
model_cnn.add(MaxPooling1D(5))
model_cnn.add(Flatten())
model_cnn.add(Dense(1, activation='sigmoid'))

model_cnn.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

cnn_history = model_cnn.fit(X_train, y_train, epochs=5, batch_size=64, validation_data=(X_test, y_test))

model_cnn.summary()

loss, accuracy = model_cnn.evaluate(X_test, y_test)
print(f'CNN Test Loss: {loss:.4f}, CNN Test Accuracy: {accuracy:.4f}')

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, Conv1D, MaxPooling1D, Flatten, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping

# Assuming you already have X_train, y_train, X_test, y_test prepared

# Define the CNN model with dropout and early stopping
model_cnn_fine_tuned = Sequential()
model_cnn_fine_tuned.add(Embedding(len(tokenizer.word_index) + 1, embedding_dim, weights=[embedding_matrix], input_length=100, trainable=False))
model_cnn_fine_tuned.add(Conv1D(256, 5, activation='relu'))
model_cnn_fine_tuned.add(MaxPooling1D(2))
model_cnn_fine_tuned.add(Flatten())
model_cnn_fine_tuned.add(Dense(128, activation='relu'))
model_cnn_fine_tuned.add(Dropout(0.5))  # Added dropout for regularization
model_cnn_fine_tuned.add(Dense(1, activation='sigmoid'))

# Compile the model
model_cnn_fine_tuned.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

# Early stopping to prevent overfitting
early_stopping = EarlyStopping(monitor='val_loss', patience=3, restore_best_weights=True)

# Train the model with early stopping
cnn_fine_history = model_cnn_fine_tuned.fit(X_train, y_train, epochs=5, batch_size=64, validation_data=(X_test, y_test), callbacks=[early_stopping])

model_cnn_fine_tuned.summary()

loss, accuracy = model_cnn_fine_tuned.evaluate(X_test, y_test)
print(f'CNN finetuned Test Loss: {loss:.4f}, CNN finetuned Test Accuracy: {accuracy:.4f}')

model_lstm = Sequential()
model_lstm.add(Embedding(len(tokenizer.word_index) + 1, embedding_dim, weights=[embedding_matrix], input_length=100, trainable=False))
model_lstm.add(LSTM(100))
model_lstm.add(Dense(1, activation='sigmoid'))

# Compile the model
model_lstm.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

# Train the model
lstm_history = model_lstm.fit(X_train, y_train, epochs=5, batch_size=64, validation_data=(X_test, y_test))

model_lstm.summary()

loss, accuracy = model_lstm.evaluate(X_test, y_test)
print(f'LSTM Test Loss: {loss:.4f}, LSTM Test Accuracy: {accuracy:.4f}')

from tensorflow.keras.layers import Bidirectional

model_bidirectional = Sequential()
model_bidirectional.add(Embedding(len(tokenizer.word_index) + 1, embedding_dim, weights=[embedding_matrix], input_length=100, trainable=False))
model_bidirectional.add(Bidirectional(LSTM(100)))
model_bidirectional.add(Dense(1, activation='sigmoid'))

model_bidirectional.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

lstmbi_history = model_bidirectional.fit(X_train, y_train, epochs=5, batch_size=64, validation_data=(X_test, y_test))

model_bidirectional.summary()

loss, accuracy = model_bidirectional.evaluate(X_test, y_test)
print(f'Test Loss: {loss:.4f}, Test Accuracy: {accuracy:.4f}')

from tensorflow.keras.layers import GRU

model_gru = Sequential()
model_gru.add(Embedding(len(tokenizer.word_index) + 1, embedding_dim, weights=[embedding_matrix], input_length=100, trainable=False))
model_gru.add(GRU(100))
model_gru.add(Dense(1, activation='sigmoid'))

model_gru.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

gru_history = model_gru.fit(X_train, y_train, epochs=5, batch_size=64, validation_data=(X_test, y_test))

model_gru.summary()

loss, accuracy = model_gru.evaluate(X_test, y_test)
print(f'Test Loss: {loss:.4f}, Test Accuracy: {accuracy:.4f}')

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, GRU, Dropout, Dense, SpatialDropout1D
from tensorflow.keras.optimizers import Adam

# Create the finetuned GRU model
model_grufine = Sequential()

# Add an Embedding layer with pre-trained word embeddings
  # Adjust the embedding dimension
model_grufine.add(Embedding(len(tokenizer.word_index) + 1,50, weights=[embedding_matrix], input_length=100, trainable=False))


model_grufine.add(GRU(128))

# Add a GRU layer with 128 units and return sequences
model_grufine.add(GRU(100, dropout=0.2, recurrent_dropout=0.2))


# Add a Dense layer with sigmoid activation for binary classification
model_grufine.add(Dense(1, activation='sigmoid'))

# Compile the model
model_grufine.compile(optimizer=Adam(learning_rate=0.001), loss='binary_crossentropy', metrics=['accuracy'])  # Adjust the learning rate

# Display the model summary
grufine_history = model_grufine.fit(X_train, y_train, epochs=5, batch_size=32, validation_data=(X_test, y_test))  # Adjust the batch size

from sklearn.metrics import precision_score, recall_score, f1_score, confusion_matrix

def calculate_metrics(y_true, y_pred):
    # Calculate precision, recall, and F1 score
    precision = precision_score(y_true, y_pred)
    recall = recall_score(y_true, y_pred)
    f1 = f1_score(y_true, y_pred)

    return precision, recall, f1

def print_metrics(model_name, y_true, y_pred):
    precision, recall, f1 = calculate_metrics(y_true, y_pred)

    print(f'Metrics for {model_name}:')
    print(f'Precision: {precision:.4f}')
    print(f'Recall: {recall:.4f}')
    print(f'F1 Score: {f1:.4f}')

y_pred_cnn = model_cnn.predict(X_test)
y_pred_lstm = model_lstm.predict(X_test)
y_pred_bilstm = model_bidirectional.predict(X_test)
y_pred_gru = model_gru.predict(X_test)

y_pred_cnn2 = model_cnn_fine_tuned.predict(X_test)
y_pred_cnn2 = (y_pred_cnn2 > 0.5).astype(int)

y_pred_gru2 = model_gru_finetuned.predict(X_test)
y_pred_gru2=(y_pred_gru2 > 0.5).astype(int)

y_pred_cnn=(y_pred_cnn > 0.5).astype(int)
y_pred_lstm=(y_pred_lstm > 0.5).astype(int)
y_pred_bilstm=(y_pred_bilstm > 0.5).astype(int)
y_pred_gru=(y_pred_gru > 0.5).astype(int)

print_metrics("CNN Fine tuned",y_test,y_pred_cnn2)

print_metrics("GRU Fine tuned",y_test,y_pred_gru2)

print_metrics("LSTM Model:", y_test, y_pred_lstm)
print_metrics("\nBiLSTM Model", y_test, y_pred_bilstm)
print_metrics("\nGRU Model", y_test, y_pred_gru)
print_metrics("\nCNN Model", y_test, y_pred_cnn)

plt.figure(figsize=(12, 4))

plt.subplot(1, 2, 1)
plt.plot(cnn_fine_history.history['accuracy'])
plt.plot(cnn_fine_history.history['val_accuracy'])
plt.title('CNN - Model Accuracy')
plt.xlabel('Epoch')
plt.ylabel('Accuracy')
plt.legend(['Train', 'Validation'], loc='upper left')
plt.subplot(1, 2, 2)
plt.plot(cnn_fine_history.history['loss'])
plt.plot(cnn_fine_history.history['val_loss'])
plt.title('CNN - Model Loss')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.legend(['Train', 'Validation'], loc='upper left')

plt.tight_layout()
plt.show()

from sklearn.metrics import confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt

# Assuming y_test and y_pred are your true labels and predicted labels, respectively
conf_mat = confusion_matrix(y_test, y_pred_cnn2)

# Plot the confusion matrix
plt.figure(figsize=(8, 6))
sns.heatmap(conf_mat, annot=True, fmt='d', cmap='Blues', cbar=False,
            xticklabels=['Negative', 'Positive'],
            yticklabels=['Negative', 'Positive'])
plt.title('CNN - Confusion Matrix')
plt.xlabel('Predicted')
plt.ylabel('True')
plt.show()

new_text = 'Not sure how Southwest in general but the check in process at Houston International was HORRIBLE. We didn’t receive help despite asking nicely and had to ask random passengers to assist us with checking in. They were too busy texting/ looking at phone. Very rude, racist customer service.'

new_text_sequence = tokenizer.texts_to_sequences([new_text])
new_text_padded = pad_sequences(new_text_sequence, maxlen=100)

# Make predictions
prediction = model_gru.predict(new_text_padded)

# If you're dealing with binary classification (sigmoid activation in the output layer)
predicted_label = 1 if prediction > 0.5 else 0

print(f"Predicted Label: {predicted_label}, Confidence: {prediction[0][0]}")