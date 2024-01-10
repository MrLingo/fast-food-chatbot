from __future__ import print_function
from flask import Flask, jsonify, render_template, request
from difflib import SequenceMatcher
from flaskr.knowledge_retreiver import domain_dict, general_dict, price_dict

from reportlab.platypus import SimpleDocTemplate, Table, Paragraph, TableStyle 
from reportlab.lib import colors 
from reportlab.lib.pagesizes import A4 
from reportlab.lib.styles import getSampleStyleSheet 

from datetime import datetime

app = Flask(__name__)

total_price = 0

# List of lists (rows that represent each bought/selected product)
product_memory = [[ "Date" , "Product", "Price (USD)" ]]

main_page_info = ["Viki", "Viki's response accuracy: ", "Total price:"]

def beautify_answer():
    pass

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

def add_record_to_payment_receipt(product_name, product_price):
   date_time_str = datetime.now().strftime("%m-%d-%Y, %H-%M-%S")   
   product_memory.append([date_time_str, product_name, product_price])
   print('updated memory:', product_memory)


@app.route('/')
def show_main_page():
    return render_template('main.html', pages=main_page_info)

@app.route('/receipt', methods=['POST'])
def generate_payment_receipt():
    '''
    DATA = [ 
        [ "Date" , "Product", "Price (USD)" ], 
        [ "16/11/2020", "", "10,999.00/-"], 
        [ "16/11/2020", "", "9,999.00/-"],
        [ "Sub Total", "", "20,9998.00/-"],
        [ "Discount", "", "-3,000.00/-"],
        [ "Total", "", "17,998.00/-"],
    ] 
    '''
    DATA = product_memory

    pdf = SimpleDocTemplate( "receipts/receipt.pdf" , pagesize = A4 ) 
    
    # standard stylesheet defined within reportlab itself 
    styles = getSampleStyleSheet() 

    title_style = styles[ "Heading1" ] 
    
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
    
    # creates a table object and passes the style to it 
    table = Table( DATA , style = style ) 
    pdf.build([ title , table ]) 
    

@app.route('/prompt', methods=['POST'])
def process_order():
    global total_price
    user_input = request.args.get('user_input')
    temp_dict = {}

    ''' Individual product price '''
    product_price = None
    

    ''' Merge knowledge '''
    domain_dict.update(general_dict)


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
            total_price = total_price + price_dict[product]
            product_price = price_dict[product]
            break


    ''' Reformating the accuracy ( show in %) '''
    accuracy = round(accuracy, 1)
    accuracy = accuracy * 100
    
    ''' Beautify answer '''
    final_answer += ' coming right away'
    response_list = [final_answer, accuracy, total_price]   
    
    add_record_to_payment_receipt(final_answer, product_price)
         
    ''' Return Viki's response to the user '''
    return jsonify(response_list)