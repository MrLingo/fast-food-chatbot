import json

''' Read config '''
with open("flaskr/static/config.json") as file:
    config_dict = json.load(file)

''' Import domain knowledge '''
with open("flaskr/static/domain_knowledge.json") as file:
    domain_dict = json.load(file)

''' Import general knowledge '''
with open("flaskr/static/general_knowledge.json") as file:
    general_dict = json.load(file)

''' Associate each product with it's price (USD) '''
with open("flaskr/static/price_mapping.json") as file:
    price_dict = json.load(file)

''' Extract products '''
with open("flaskr/static/products.json") as file:
    products_objs_dict = json.load(file)


def add_path_to_img_names() -> None:
    for product in products_objs_dict:
        product["src_name"] = "static/database/" + product["type"] + "/" + product["src_name"]
        print('SRC NAME:', product["src_name"])

add_path_to_img_names()