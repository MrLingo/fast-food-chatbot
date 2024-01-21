from __future__ import print_function
import hashlib
from nltk import ngrams
import pandas as pd
from datetime import datetime
from flask import Flask, jsonify, render_template, request
from reportlab.platypus import SimpleDocTemplate, Table
from reportlab.lib.pagesizes import A4 
from flaskr.knowledge_retreiver import domain_dict, general_dict, price_dict
from flaskr.topic_extractor import extract_topic
from flaskr.product_extractor import extract_products, store_extracted_products
from flaskr.get_images_model import collect_products
from flaskr.intent_handler import match_images_intent, catch_product_count_ordered, do_levenstein
from flaskr.receipt_builder import build_receipt_template
from flaskr.autocomplete_handler import store_input_for_autocomplete, autocomplete_path


app = Flask(__name__)

total_price: float = 0
product_memory: list= [[ 'Date' , 'Product', 'Price (USD)' ]]
main_page_info: list = ['Viki', 'Viki\'s response accuracy: ', 'Total price:']
date_time_str: str = None


def add_record_to_payment_receipt(user_input: str, product_name: str, product_price: str) -> None:
   n_products = catch_product_count_ordered(user_input)
   date_time_str = datetime.now().strftime('%m-%d-%Y, %H-%M-%S')
  
   print('n_products', n_products)
   for _ in range(n_products):
       product_memory.append([date_time_str, product_name, product_price])    


def calculate_total_price(final_answer: str) -> float:
    global total_price

    for product in price_dict:        
        if product.lower() in final_answer.lower():
            total_price += price_dict[product]
            return price_dict[product]
    return 0.0


# ======================================== Routes ========================================


@app.route('/')
def show_main_page():
    return render_template('main.html', pages=main_page_info)


@app.route('/autocomplete', methods=['GET'])
def autocomplete():
    user_input = request.args.get('user_input')

    words = user_input.split()
    if len(words) >= 2:
        bigrams = ngrams(words, 2)

        ''' 
        Uncomment for debugging 
        for bigram in bigrams:
            print('PREFIX INPUT: ', bigram[0])
            print('SUFFIX INPUT: ', bigram[1])
            print(' =================== ')
        '''
         
        autocmpl_df = pd.read_excel(autocomplete_path, sheet_name='main')
        row = autocmpl_df[autocmpl_df['Prefix'] == user_input]

        if not row.empty:
            return jsonify([row['Suffix'].values[0]])

    return jsonify(['No suggestion found'])


@app.route('/receipt', methods=['GET'])
def generate_payment_receipt():
    # Build name, using hash and the current datetime as an order identifier.
    date_time_str = datetime.now().strftime('%m-%d-%Y, %H-%M-%S')
    order_num_hash = str(hashlib.sha256(date_time_str.encode()).hexdigest()[:8]).upper()

    receipt_data = product_memory
    receipt_data.append([ 'Total', '', str(total_price)])    
    receipt_name = f'viki_receipt_order_{order_num_hash}_{date_time_str}.pdf'

    pdf = SimpleDocTemplate(f'receipts/{receipt_name}' , pagesize = A4 )     
    title, style = build_receipt_template()
    
    # Create a table object and pass the style to it.
    table = Table(receipt_data , style = style )
    pdf.build([title, table ])

    # Validate receipt storage.
    receipt_list = [receipt_name]
    print(receipt_data, len(receipt_data))

    if len(receipt_data) > 1:
        receipt_list.append('receipt.pdf generated')
    else:
        receipt_list.append('No data')
    
    # Reset the product memory.
    product_memory[1:] = []
    return jsonify(receipt_list)
    

@app.route('/prompt', methods=['POST'])
def process_order():
    global total_price
    product_price = None

    try:
        data = request.form
        user_input = data.get('user_input')
    except Exception as e:
        pass
        print('Error handling POST request via /prompt endpoint', e)

    # Merge knowledge.
    domain_dict.update(general_dict)
    store_input_for_autocomplete(user_input)

    # Do Levenstein and calculation of price.
    final_answer, accuracy = do_levenstein(domain_dict, user_input)
    product_price = calculate_total_price(final_answer)
     
    # Extract topic.
    topic_words, topic_extraction_type = extract_topic(user_input)
    extracted_products = extract_products(topic_words=topic_words, products_dict=price_dict, topic_type=topic_extraction_type)
    store_extracted_products(extracted_products)

    '''
    Capture product type, based on what the user wants to see and
    display the respective product's images.
    '''
    product_type = match_images_intent(user_input)
    products_to_return = collect_products(product_type=product_type)
    print('PRODUCTS TO RETURN: ', products_to_return) 
    
    # Prepare the data for UI.
    final_answer += ' coming right away'
    response_list = [final_answer, accuracy, total_price, topic_words, topic_extraction_type, products_to_return]   
    
    add_record_to_payment_receipt(user_input, final_answer.replace('coming right away', '').strip(), product_price)         
    return jsonify(response_list)


if __name__ == '__main__':
    app.run(port="5000")