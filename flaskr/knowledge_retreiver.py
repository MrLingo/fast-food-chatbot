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