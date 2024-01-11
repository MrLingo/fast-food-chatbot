from __future__ import print_function
from flask import Flask, jsonify, render_template, request
from difflib import SequenceMatcher
from flaskr.knowledge_retreiver import domain_dict, general_dict, price_dict
import hashlib
from nltk import ngrams
from openpyxl import load_workbook
import pandas as pd

from reportlab.platypus import SimpleDocTemplate, Table, Paragraph, TableStyle 
from reportlab.lib import colors 
from reportlab.lib.pagesizes import A4 
from reportlab.lib.styles import getSampleStyleSheet 

from datetime import datetime

app = Flask(__name__)

total_price : float = 0

# List of lists (rows that represent each bought/selected product)
product_memory : list= [[ "Date" , "Product", "Price (USD)" ]]
main_page_info : list = ["Viki", "Viki's response accuracy: ", "Total price:"]
date_time_str : str = None
autocomplete_path : str = r'flaskr/static/autocomplete_memory.xlsx'


def write_to_excel_autocomplete(prefix, suffix) -> None:
    new_row_data = [prefix, suffix]
    wb = load_workbook(autocomplete_path)

    # Select first worksheet
    ws = wb.worksheets[0]

    ws.append(new_row_data)
    wb.save(autocomplete_path)


def store_input_for_autocomplete(user_input) -> None:
    # If input long enough (at least three words) - build trigrams
    words = user_input.split()
    if len(words) >= 3:
        trigrams = ngrams(words, 3)

        for trigram in trigrams:
            print('first part ', trigram[0])
            print('second part ', trigram[1])
            print('third part ', trigram[2])
            print(' =================== ')

        prefix = trigram[0] + " " + trigram[1]
        suffix = trigram[2]
        write_to_excel_autocomplete(prefix, suffix)


def beautify_answer():
    pass


def similar(a, b) -> float:
    return SequenceMatcher(None, a, b).ratio()


def add_record_to_payment_receipt(product_name, product_price) -> None:
   date_time_str = datetime.now().strftime("%m-%d-%Y, %H-%M-%S")   
   product_memory.append([date_time_str, product_name, product_price])
   print('Updated memory:', product_memory)


def build_receipt_template():
    # standard stylesheet defined within reportlab itself 
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


def calculate_total_price(final_answer):
    global total_price

    for product in price_dict:        
        if product.lower() in final_answer.lower():
            total_price += price_dict[product]
            return price_dict[product]


def do_levenstein(domain_dict, user_input):
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


# ============================== Routes =======================================


@app.route('/')
def show_main_page():
    return render_template('main.html', pages=main_page_info)


@app.route('/autocomplete', methods=['GET'])
def autocomplete():
    user_input = request.args.get('user_input')

    words = user_input.split()
    if len(words) >= 2:
        bigrams = ngrams(words, 2)

        for bigram in bigrams:
            print('PREFIX INPUT: ', bigram[0])
            print('SUFFIX INPUT: ', bigram[1])
            print(' =================== ')
         
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
        print("Data received successfully", user_input)
    except Exception as e:
        print("Error handling POST request via /prompt endpoint", e)

    ''' Merge knowledge '''
    domain_dict.update(general_dict)

    ''' Store for future autocompletion '''
    store_input_for_autocomplete(user_input)

    final_answer, accuracy = do_levenstein(domain_dict, user_input)
    product_price = calculate_total_price(final_answer)
     
    ''' Beautify answer '''
    final_answer += ' coming right away'
    response_list = [final_answer, accuracy, total_price]   
    
    add_record_to_payment_receipt(final_answer.replace('coming right away', '').strip(), product_price)
         
    ''' Return Viki's response to the user '''
    return jsonify(response_list)


if __name__ == "__main__":
    app.run(port="5000")