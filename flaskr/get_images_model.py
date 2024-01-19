from flaskr.knowledge_retreiver import products_objs_dict

def collect_products(product_type : str) -> list:
    products_to_return_list = []
    products_to_return_list = [product for product in products_objs_dict if product["type"] == product_type]
    return products_to_return_list