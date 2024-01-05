
import json

''' Import domain knowledge '''
with open("static/domain_knowledge.json") as file:
    domain_dict = json.load(file)

''' Import general knowledge '''
with open("static/general_knowledge.json") as file:
    general_dict = json.load(file)

''' Associate each product with it's price (USD) '''
with open("static/price_mapping.json") as file:
    price_dict = json.load(file)