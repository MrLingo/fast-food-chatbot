from __future__ import print_function
from flask import Flask, jsonify, render_template, request
from difflib import SequenceMatcher
from flaskr.knowledge_retreiver import domain_dict, general_dict, price_dict, config_dict
from flaskr.topic_extractor import extract_topic
from flaskr.product_extractor import extract_products, store_extracted_products
import hashlib
from nltk import ngrams
from openpyxl import load_workbook
import pandas as pd
from reportlab.platypus import SimpleDocTemplate, Table, Paragraph, TableStyle 
from reportlab.lib import colors 
from reportlab.lib.pagesizes import A4 
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime
import re
from flaskr.get_images_model import collect_products

app = Flask(__name__)

total_price : float = 0
product_memory : list= [[ "Date" , "Product", "Price (USD)" ]]
main_page_info : list = ["Viki", "Viki's response accuracy: ", "Total price:"]
date_time_str : str = None
autocomplete_path : str = config_dict['autocomplete_memory_path']


def write_to_excel_autocomplete(prefix, suffix) -> None:
    new_row_data = [prefix, suffix]
    wb = load_workbook(autocomplete_path)

    # Select first worksheet
    ws = wb.worksheets[0]

    ws.append(new_row_data)
    wb.save(autocomplete_path)


# Can be extracted outside
def store_input_for_autocomplete(user_input) -> None:
    # If input long enough (at least three words) - build trigrams
    words = user_input.split()
    if len(words) >= 3:
        trigrams = ngrams(words, 3)

        for trigram in trigrams:
            #print('first part ', trigram[0])
            #print('second part ', trigram[1])
            #print('third part ', trigram[2])
            print(' =================== ')

        prefix = trigram[0] + " " + trigram[1]
        suffix = trigram[2]
                
        write_to_excel_autocomplete(prefix, suffix)


def beautify_answer():
    pass


def similar(a, b) -> float:
    return SequenceMatcher(None, a, b).ratio()


# Can be extracted outside
# Catches how many of certain product does the user wants to order
def catch_product_count_ordered(user_input : str) -> int:
    regex1 = '(Give me|I want|I would like to order) (\d+)'
    regex2 = '(and \d+|^\d+)'
    product_count = 1
    regex_list = [regex1, regex2]

    for regex in regex_list:
        matches = re.findall(regex, user_input, flags=re.I)

        # Every tuple
        for match in matches:
            # Evert tuple element
            for m in match:
                if re.findall('\d+', m):
                    product_count = re.findall('\d+', m)[0]
            
    return int(product_count)


# Can be extracted outside
def add_record_to_payment_receipt(user_input : str, product_name : str, product_price : str) -> None:
   n_products = catch_product_count_ordered(user_input)
   date_time_str = datetime.now().strftime("%m-%d-%Y, %H-%M-%S")
  
   print('n_products', n_products)
   for _ in range(n_products):
       product_memory.append([date_time_str, product_name, product_price])    


# Can be extracted outside
def build_receipt_template():
    # Standard stylesheet defined within reportlab itself 
    styles = getSampleStyleSheet() 

    title_style = styles[ "Heading1" ] 
    
    ''' 
    Template reference

    DATA = [ 
        [ "Date" , "Product", "Price (USD)" ], 
        [ "16/11/2020", "", "10,999.00/-"], 
        [ "16/11/2020", "", "9,999.00/-"],
        [ "Sub Total", "", "20,9998.00/-"],
        [ "Discount", "", "-3,000.00/-"],
        [ "Total", "", "17,998.00/-"],
    ] 

    '''

    # 0: left, 
    # 1: center, 
    # 2: right 
    title_style.alignment = 1
    
    title = Paragraph( "Payment receipt - Viki" , title_style ) 
    
    style = TableStyle( 
        [ 
            ( "BOX" , ( 0, 0 ), ( -1, -1 ), 1 , colors.black ), 
            ( "GRID" , ( 0, 0 ), ( 4 , 4 ), 1 , colors.black ), 
            ( "BACKGROUND" , ( 0, 0 ), ( 3, 0 ), colors.gray ), 
            ( "TEXTCOLOR" , ( 0, 0 ), ( -1, 0 ), colors.black ), 
            ( "ALIGN" , ( 0, 0 ), ( -1, -1 ), "CENTER" ), 
            ( "BACKGROUND" , ( 0 , 1 ) , ( -1 , -1 ), colors.white ), 
        ] 
    ) 
    
    return title, style


def calculate_total_price(final_answer : str):
    global total_price

    for product in price_dict:        
        if product.lower() in final_answer.lower():
            total_price += price_dict[product]
            return price_dict[product]


# Can be extracted outside
def do_levenstein(domain_dict : dict, user_input : str):
    temp_dict = {}
    ''' Traversing data dict and filling a temporary one (answer : ratio). '''
    for i in domain_dict:
        ratio = similar(i, user_input.lower())
        temp_dict[domain_dict[i]] = ratio

    ''' Choosing the one with the best ratio from the generated one. '''
    final_answer = max(temp_dict, key=temp_dict.get)
    accuracy = temp_dict[final_answer]
    
    ''' Show accuracy in % '''
    accuracy = round(accuracy, 1)
    accuracy = accuracy * 100

    return final_answer, accuracy


# Can be extracted outside
def match_images_intent(user_input : str) -> str:
    # Categories:
    categories = '(drinks|pizzas|burgers|products)'
    product_type = ""

    regex1 = f'show me {categories}*(all your )*{categories}*'
    regex2 = f'what (are all the |are the )*{categories}( do|can )* you offer'
    regex3 = f'I would like to (see|know)( all )* your {categories}'
    regex4 = f'I want to (see|know) all your {categories}'

    # Try with every regex:
    regex_list = [regex1, regex2, regex3, regex4]

    for regex in regex_list:        
        matches = re.findall(regex, user_input, flags=re.I)
        print('matches', matches)

        for match in matches:
            if "pizza" in match or "pizzas" in match:
                product_type = "pizza"                
            elif "burger" in match or "burgers" in match:
                product_type = "burger"
            elif "drink" in match or "drinks" in match:
                product_type = "drink"
            else:
                product_type = ""
        
    return product_type


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

        ''' Uncomment for debugging 
        for bigram in bigrams:
            print('PREFIX INPUT: ', bigram[0])
            print('SUFFIX INPUT: ', bigram[1])
            print(' =================== ')
        '''
         
        autocmpl_df = pd.read_excel(autocomplete_path, sheet_name='main')
        row = autocmpl_df[autocmpl_df["Prefix"] == user_input]

        if not row.empty:
            return jsonify([row['Suffix'].values[0]])

    return jsonify(["No suggestion found"])


@app.route('/receipt', methods=['GET'])
def generate_payment_receipt():
    # Build name, using hash + current datetime as an order identifier 
    date_time_str = datetime.now().strftime("%m-%d-%Y, %H-%M-%S")
    order_num_hash = str(hashlib.sha256(date_time_str.encode()).hexdigest()[:8]).upper()

    receipt_data = product_memory
    receipt_data.append([ "Total", "", str(total_price)])
    
    receipt_name = f"viki_receipt_order_{order_num_hash}_{date_time_str}.pdf"

    pdf = SimpleDocTemplate(f"receipts/{receipt_name}" , pagesize = A4 ) 
    
    title, style = build_receipt_template()
    
    # Creates a table object and passes the style to it 
    table = Table(receipt_data , style = style )
    pdf.build([title , table ])

    # Validate receipt storage
    receipt_list = [receipt_name]
    print(receipt_data, len(receipt_data))

    if len(receipt_data) > 1:
        receipt_list.append("receipt.pdf generated")
    else:
        receipt_list.append("No data")

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
        print("Error handling POST request via /prompt endpoint", e)

    # Merge knowledge
    domain_dict.update(general_dict)
    store_input_for_autocomplete(user_input)

    final_answer, accuracy = do_levenstein(domain_dict, user_input)
    product_price = calculate_total_price(final_answer)
     
    topic_words, topic_extraction_type = extract_topic(user_input)
    extracted_products = extract_products(topic_words=topic_words, products_dict=price_dict, topic_type=topic_extraction_type)
    #print('extracted products: ', extracted_products)
    store_extracted_products(extracted_products)

    # Capture product type, based on what the user wants to see.
    # E.g. "Show me all your drinks"
    # Show or not show images from DB
    product_type = match_images_intent(user_input)
    #product_type = "drink"

    products_to_return = collect_products(product_type=product_type)
    print("PRODUCTS TO RETURN: ", products_to_return) 
    

    ''' Beautify answer '''
    final_answer += ' coming right away'
    response_list = [final_answer, accuracy, total_price, topic_words, topic_extraction_type, products_to_return]   
    
    add_record_to_payment_receipt(user_input, final_answer.replace('coming right away', '').strip(), product_price)         
    return jsonify(response_list)


if __name__ == "__main__":
    app.run(port="5000")