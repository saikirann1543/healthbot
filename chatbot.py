import random
import re
import spacy
from spacy.lang.en.stop_words import STOP_WORDS
from gensim.models import KeyedVectors
import pandas as pd
import csv
# load pre-trained word2vec model
w2v_model = KeyedVectors.load_word2vec_format("Cone.bin", binary=True, encoding='ansi')

# load spacy nlp model
nlp = spacy.load('en_core_web_sm/', disable=['ner', 'parser'])
dataset = pd.read_csv("oneyo.csv", encoding="latin-1")

# remove duplicate question
dataset = dataset.drop_duplicates(subset='Questions', keep='first')


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
    # print(question)

    for quest in dataset["Questions"]:
        # preprocess dataset question
        q = preprocess_text(str(quest))
        # print("Here is q")
        # print(q)
        # print("Here is question", '                                           ', q.split())
        # calculate similarity using word2vec
        try:
            if q:
                score = w2v_model.n_similarity(question.split(), q.split())
            # print(score)
        except KeyError:
            score = -1

        if score > max_score:
            max_score = score
            closest_question = quest
            # print(closest_question)

    if max_score >= threshold:
        # print(closest_question)
        return closest_question
    else:
        return None

# random_qes = dataset['Questions'][random.randint(0, len(dataset['Questions']) - 1)]
# print(random_qes)
# question = get_closest_question("have you noticed any weight loss or fever")
# print(question)


def get_dataset_response(question):
    # Check if input is in dataset or closest matching question is in dataset
    category = dataset.loc[dataset['Questions'].str.lower() == question.lower(), 'Category'].values
    closest_question = get_closest_question(question)
    if closest_question is not None:
        question = closest_question
        # print("Here is the closest question")
        # print(question)
    else:
        return "Please ask relevant questions!", dataset['Questions'][random.randint(0, len(dataset['Questions']) - 1)]

    dataset_indexed = dataset.set_index('Questions')


    try:
        row = dataset_indexed.loc[question]
       
    except KeyError:
        return None
    # exit()
    response_type = row['Yes Type'] if random.random() < 0.5 else row['No Type']
    # response = row['Yes Type'] if (response_type == 'Yes Type' or str(row['Category'][1]).startswith("Scenario")) else row['No Type']
    if str(row['Category']).startswith("Sce"):
        response = row['Yes Type']
    elif str(row['Category']).startswith("Sce"):
        response = row['Yes Type']
    elif response_type == 'Yes Type':
        response = row['Yes Type']
    else:
        response = row['No Type']

    try:
        return response, closest_question
    except TypeError:
        return response, closest_question

covered_categories = []
    #
    # # Initialize dictionary of bottom questions
bottom_questions = {}
while True:
        # Get input from doctor
        question = input(f":Doctor ")
        # question = "how do you feel now?"
    
        if question.lower() in ["end", "stop", "quit", "exit", "bye"]:
            rating = input("Please rate the chatbot from 1 to 5: ")
            print(f"Thank you for using the chatbot! You rated it {rating}/5.")
            
            # Store username and rating in CSV file
            with open("ratings.csv", mode="a", newline="\n") as file:
                writer = csv.writer(file)
                writer.writerow([rating])
            
            # Thank the user for chatting
            print(f"Thank you for chatting with me!")
            break
        # Check if input is in dataset or closest matching question is in dataset
    
        response, closest_question = get_dataset_response(question)
    
        if response is not None:
            # Return response from dataset
            print("Chatbot:", response)
            category = dataset.loc[dataset["Questions"] == closest_question, "Category"].iloc[0]
            if category not in covered_categories:
                covered_categories.append(category)
                # Store a bottom question for the category
                bottom_questions[category] = dataset.loc[dataset["Category"] == category].sample()["Questions"].iloc[0]
        
    
        else:    
            # Return response from chatbot
            print("Chatbot: I don't understand. Please ask another question.")
        
        
