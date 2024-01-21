import re
from difflib import SequenceMatcher


def match_images_intent(user_input: str) -> str:
    categories = '(drinks|pizzas|burgers|products)'
    product_type = ''

    regex1 = f'show me {categories}*(all your )*{categories}*'
    regex2 = f'what (are all the |are the )*{categories}( do|can )* you offer'
    regex3 = f'I would like to (see|know)( all )* your {categories}'
    regex4 = f'I want to (see|know) all your {categories}'

    # Try with every regex.
    regex_list = [regex1, regex2, regex3, regex4]

    for regex in regex_list:        
        matches = re.findall(regex, user_input, flags=re.I)
        print('matches', matches)

        for match in matches:
            if 'pizza' in match or 'pizzas' in match:
                product_type = 'pizza'                
            elif 'burger' in match or 'burgers' in match:
                product_type = 'burger'
            elif 'drink' in match or 'drinks' in match:
                product_type = 'drink'
            else:
                product_type = ''
        
    return product_type


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