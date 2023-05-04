import random
from flask import Flask, render_template, request, jsonify
from try2 import get_dataset_response, get_category_and_rating
import json
import csv
import os
app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def chatbot():
    return render_template('base.html')

@app.post('/predict')
def predict():
    try:
        text = request.get_json().get('message')
        if text.lower() in ["end", "stop", "quit", "exit", "bye"]:
            pass
        print("this is the text", text)
        if text.lower() in ["hi", "hello doc!", "hey", "hi there", "hello there", "Hey there"]:
            messages = ["Hello Doc!", "Hi Doc!", 'Hello, how are you feeling today?', 'Hi, how can I help you today?', 'Hey, how are you doing today?']
            message = {'answer': random.choice(messages)}
            return jsonify(json.loads(json.dumps(message, indent=4)))
        respo = get_dataset_response(text)
        response = respo[0]
        print("this is the response", response)
        closest_question = respo[1]
        message = {'answer': response}
        print("this is the messsage", message)
        if text.lower() in ["end", "stop", "quit", "exit", "bye"]:
            category = get_category_and_rating(response, closest_question)
            output_string = ' & '.join(category)
            message = {'answer': f"Thank you for chatting with me!. I hope I was able to help you with your problem. \n {output_string} "}
            return jsonify(json.loads(json.dumps(message, indent=4)))
        else:
            return jsonify(message)
        
    except Exception as e:
        return jsonify({'answer': e})
    

@app.route('/rating', methods=['POST'])
def save_rating():
    data = request.json
    name = data['name']
    rating = data['rating']
    if os.path.exists('ratings.csv'):
        with open('ratings.csv', mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([name, rating])
            response = {'message': 'Rating saved successfully!'}
            print("Rating saved successfully!")
    else:
        os.system('touch ratings.csv')
   
    return jsonify(response)


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')
                          
