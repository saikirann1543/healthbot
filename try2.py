import pandas as pd
import openai
import random
import csv
import spacy
import re
from spacy.lang.en.stop_words import STOP_WORDS
from gensim.models import KeyedVectors
from flask import Flask, request, jsonify, render_template


w2v_model = KeyedVectors.load_word2vec_format('new_another_one.bin', binary=True)

# load spacy nlp model
nlp = spacy.load('en_core_web_sm', disable=['ner', 'parser'])
# Load dataset from CSV file into pandas DataFrame
dataset = pd.read_csv("one.csv", encoding="latin-1")
# Define function to get the closest matching question from dataset using spaCy's similarity score
def preprocess_text(text):
    # lowercase text
    text = text.lower()

    # remove punctuations and digits
    text = re.sub(r'[^a-zA-Z\s]', '', text)

    # remove stop words
    text = " ".join([word for word in text.split() if word not in STOP_WORDS])

    # lemmatize text
    doc = nlp(text)
    text = " ".join([token.lemma_ for token in doc])

    return text



def get_closest_question(question, threshold=0.7):
    max_score = -1
    closest_question = None

    # preprocess user input
    question = preprocess_text(question)

    for quest in dataset["Questions"]:
        # preprocess dataset question
        q = preprocess_text(str(quest))
        # print(q)

        # calculate similarity using word2vec
        try:
            score = w2v_model.n_similarity(question.split(), q.split())
        except KeyError:
            score = -1

        if score > max_score:
            max_score = score
            closest_question = quest

    if max_score >= threshold:
        return closest_question
    else:
        return None

def get_dataset_response(question):
    # Check if input is in dataset or closest matching question is in dataset
    category = dataset.loc[dataset['Questions'].str.lower() == question.lower(), 'Category'].values
    closest_question = get_closest_question(question)
    if closest_question is not None:
        question = closest_question
    else:
        return "Please ask relevant questions!", dataset['Questions'][random.randint(0, len(dataset['Questions']) - 1)]

    dataset_indexed = dataset.set_index('Questions')

    try:
        row = dataset_indexed.loc[question]
        # print(row)
    except KeyError:
        return None
    # exit()
    response_type = row['Yes Type'] if random.random() < 0.5 else row['No Type']
    # response = row['Yes Type'] if (response_type == 'Yes Type' or str(row['Category'][1]).startswith("Scenario")) else row['No Type']
    if "Scenario 1" in str(row['Category']):
        response = row['Yes Type']
    elif "Scenario 2" in str(row['Category']):
        response = row['Yes Type']
    elif response_type == 'Yes Type':
        response = row['Yes Type']
    else:
        response = row['No Type']

    try:
        return response, closest_question
    except TypeError:
        return response, closest_question

# Define function to get response from OpenAI API
    # Use OpenAI API to generate response
    question = "answer this question as if a doctor is asking you \n" + question
    response = openai.Completion.create(
        engine="davinci",
        prompt=question,
        max_tokens=50,
        n=1,
        stop=".",
        temperature=0.2,
    )

    return response.choices[0].text.strip()

# Initialize list of covered categories
covered_categories = []

# Initialize dictionary of bottom questions
bottom_questions = {}

import random

def get_category_and_rating(response, closest_question):
    # Your code here
    # I assume that the "get_dataset_response" and "get_openai_response" functions
    # are defined elsewhere and are working correctly
    covered_categories = []
    bottom_questions = {}
    if response is not None:
        # Return response from dataset
        category = dataset.loc[dataset["Questions"] == closest_question, "Category"].iloc[0]
        if category not in covered_categories:
            covered_categories.append(category)
            # Store a bottom question for the category
            bottom_questions[category] = dataset.loc[dataset["Category"] == category].sample()["Questions"].iloc[0]

    uncovered_categories = list(set(dataset["Category"]) - set(covered_categories))
    questions = []
    if len(uncovered_categories) > 0:
        for category in uncovered_categories:
            category_questions = dataset.loc[dataset["Category"] == category]
            if not category_questions.empty:
                random_question = category_questions.sample()["Questions"].iloc[0]
                questions.append(random_question)
    return questions

# run the flask app on / route
if __name__ == "__main__":
    print('hello')
