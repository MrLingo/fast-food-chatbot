from __future__ import print_function
from flask import Flask, json, jsonify, render_template, request
from difflib import SequenceMatcher

app = Flask(__name__)

main_page_info = ["Viki", "Viki's response accuracy: ", "Total price:"]

@app.route('/')
def hello_world():
    return render_template('main.html', pages=main_page_info)


def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()


total_price = 0

''' Associate each product with it's price (USD)  '''
price_dict = {
      "Pepperoni": 1,
      "Margherita" : 1.5,
      "White Pizza": 1,
      "Caesar Salad Pizza": 2.5,
      "Venetian Rolled": 2,
      "Pizza Pockets": 1.3,
      "Calzone": 1.5,
      "Griddled California Pizzas": 2.4,
      "Bruscheta Pizzaiola": 2.1,
      "Breakfast Pizza": 1.5,
      "Gluten-free Mushroom": 1.6,
      "Wingless Buffalo Chicken": 2 ,
      
      "Big Mac": 2.5,
      "Quarter Pounder": 2,
      "Cheeseburger": 1.5,
      "Hamburger": 1.3,

      "Bacon Ranch Salad": 3,
      "Side Salad": 2.7,
      "Coca-Cola": 1,
      "Sprite": 1,
      "Fanta": 1,
      "Orange": 1.2,
      "Dasani water": 0.6
    }

@app.route('/data')
def process_order():
    global total_price
    user_input = request.args.get('user_input')
    temp_dict = {}

    with open("static/database.json") as file:
        data_dict = json.load(file)

    
    ''' Traversing data dict and filling a temporary one ( answer:ratio ). '''
    for i in data_dict:
        ratio = similar(i, user_input.lower())
        temp_dict[data_dict[i]] = ratio


    ''' Choosing the one with the best ratio from the generated one. '''
    final_answer = max(temp_dict, key=temp_dict.get)
    accuracy = temp_dict[final_answer]
    
    ''' Calculating total price. '''
    for product in price_dict:
        if product in final_answer:
            total_price = total_price + price_dict[product]

    ''' Reformating the accuracy ( show in %) '''
    accuracy = round(accuracy, 1)
    accuracy = accuracy * 100
    response_list = [final_answer, accuracy, total_price]          

    ''' Return Viki's response to the user! '''
    return jsonify(response_list)
