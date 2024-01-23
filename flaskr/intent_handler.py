import re
from difflib import SequenceMatcher
import joblib


SHOW_ALL_PRODUCTS_INTENT = 'Show all products'
SHOW_PRODUCT_CATEGORY_INTENT = 'Show product category'
SHOW_SPECIFIC_PRODUCT_INTENT = 'Show specific product'
ORDER_PRODUCT_INTENT = 'Order a product'
OTHER_INTENT = 'Other'

BURGER_CATEGORY = 'burger'
DRINK_CATEGORY = 'drink'
PIZZA_CATEGORY = 'pizza'


def predict_intent(user_input: str) -> str:
    # Load the model and it's vectorizer.
    nb_classifier = joblib.load('model/intent_recognition_model_viki.joblib')
    vectorizer = joblib.load('model/intent_recognition_model_viki_vectorizer.joblib')

    X_new = vectorizer.transform([user_input])   
    predicted_intent = nb_classifier.predict(X_new)
    print(f"Predicted Intent: {predicted_intent[0]}")
    return predicted_intent[0]

'''
Seperation logic:
If intent = Other -> not_recognized()
If intent = Show all products -> show_products(intent)
If intent = Show product categories -> show_products(intent)
If intent = Show specific product -> show_products(intent)
If intent = Order product -> do_levenstein(dict, intent)
'''


def not_recognized() -> str:
    return 'I am sorry, but I don\'t know how to answer that'


def show_products(intent: str, user_input: str) -> str:
    if intent == SHOW_ALL_PRODUCTS_INTENT:
        print('show all products')
        return 'show_all'                    
    elif intent == SHOW_PRODUCT_CATEGORY_INTENT:
        print('show product category')
        matches = re.findall(f'({DRINK_CATEGORY}|{PIZZA_CATEGORY}|{BURGER_CATEGORY})+', user_input)
        
        if matches is not None and len(matches) > 0:
            for match in matches:
                if match == DRINK_CATEGORY:
                    product_type = DRINK_CATEGORY
                elif match == BURGER_CATEGORY:
                    product_type = BURGER_CATEGORY
                elif match == PIZZA_CATEGORY:
                    product_type = PIZZA_CATEGORY
                else:
                    product_type = ''
        else:
            product_type = ''
        return product_type    
    elif intent == SHOW_SPECIFIC_PRODUCT_INTENT:
        extracted_product = re.findall('', intent)
        print('show specific product') # -> traverse the whole domain dict for keyword match with the one extracted from intent. If domain dict product is inside intent -> match

        # for product_intent in domain_dict:
        #     if product_intent.lower() in extracted_product[0]
        #         return product_name                              

        # Then, after returned -> 
        # for product in products_objs_dict 
        #     if product['name'].lower() == product_name:
        #         products_to_return = [product]

        return 'specific_product' 
    elif intent == ORDER_PRODUCT_INTENT:
        print('order_product')
        return 'order_product' # -> do_levenstein
    else:
        print('other')
        return 'other'


# Catches how many of certain product does the user wants to order.
def catch_product_count_ordered(user_input: str) -> int:
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


def do_levenstein(domain_dict: dict, user_input: str) -> tuple[str, int]:
    temp_dict = {}
    # Traversing data dict and filling a temporary one (answer : ratio).
    for i in domain_dict:
        ratio = similar(i, user_input.lower())
        temp_dict[domain_dict[i]] = ratio

    # Choosing the one with the best ratio from the generated one.
    final_answer = max(temp_dict, key=temp_dict.get)
    accuracy = temp_dict[final_answer]
    
    # Show accuracy in %.
    accuracy = round(accuracy, 1)
    accuracy = accuracy * 100

    return final_answer, accuracy


def similar(a, b) -> float:
    return SequenceMatcher(None, a, b).ratio()


def beautify_answer():
    pass