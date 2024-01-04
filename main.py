from __future__ import print_function
from flask import Flask, json, jsonify, render_template, request
from difflib import SequenceMatcher
from knowledge_retreiver import domain_dict, general_dict, price_dict

app = Flask(__name__)

main_page_info = ["Viki", "Viki's response accuracy: ", "Total price:"]

@app.route('/')
def show_main_page():
    return render_template('main.html', pages=main_page_info)

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()


total_price = 0

@app.route('/data')
def process_order():
    global total_price
    user_input = request.args.get('user_input')
    temp_dict = {}
    
    ''' Traversing data dict and filling a temporary one ( answer:ratio ). '''
    for i in domain_dict:
        ratio = similar(i, user_input.lower())
        temp_dict[domain_dict[i]] = ratio


    ''' Choosing the one with the best ratio from the generated one. '''
    final_answer = max(temp_dict, key=temp_dict.get)
    accuracy = temp_dict[final_answer]
    
    
    ''' Calculating total price. '''
    for product in price_dict:        
        if product.lower() in final_answer.lower():
            print('total price:' , round(total_price, 2))
            print()
            total_price = total_price + price_dict[product]

    ''' Reformating the accuracy ( show in %) '''
    accuracy = round(accuracy, 1)
    accuracy = accuracy * 100
    response_list = [final_answer, accuracy, total_price]          

    ''' Return Viki's response to the user '''
    return jsonify(response_list)