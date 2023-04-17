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
        respo = get_dataset_response(text)
        response = respo[0]
        closest_question = respo[1]
        message = {'answer': response}
        if text.lower() in ["end", "stop", "quit", "exit", "bye"]:
            category = get_category_and_rating(response, closest_question)
            output_string = '\n\n'.join(category)
            message = {'answer': f"Thank you for chatting with me!. I hope I was able to help you with your problem. \n {output_string} "}
            return jsonify(json.loads(json.dumps(message, indent=4)))
        else:
            return jsonify(message)
    except Exception as e:
        return jsonify({'answer': e})
    

@app.route('/rating', methods=['POST'])
def save_rating():
    response = {}
    data = request.json
    name = data['name']
    rating = data['rating']
    if not os.path.exists('ratings.csv'):
        with open('ratings.csv', mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Name', 'Rating'])
            writer.writerow([name, rating])
            response = {'message': 'Rating saved successfully!'}
            print("Rating saved successfully!")
            return jsonify(response)

    if os.path.exists('ratings.csv'):
        with open('ratings.csv', mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([name, rating])
            response = {'message': 'Rating saved successfully!'}
            print("Rating saved successfully!")
            return jsonify(response)   
    return jsonify(response)


@app.route('/show_ratings', methods=['GET'])
def show_ratings():
    response = {}
    if os.path.exists('ratings.csv'):
        with open('ratings.csv', mode='r') as file:
            reader = csv.reader(file)
            response = {'ratings': list(reader)}
    return render_template('show_ratings.html', response=response)

@app.route('/show_ratings_json', methods=['GET'])
def show_ratings_json():
    if os.path.exists('ratings.csv'):
        with open('ratings.csv', mode='r') as file:
            reader = csv.reader(file)
            response = {'ratings': list(reader)}
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')
