from flaskr.knowledge_retreiver import products_objs_dict


def collect_products(product_type: str) -> list:
    if product_type != 'show_all':
        return [product for product in products_objs_dict if product['type'] == product_type]
    else:
        return products_objs_dict