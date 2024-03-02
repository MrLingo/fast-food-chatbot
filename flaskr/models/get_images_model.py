from flaskr.models.knowledge_retreiver_model import products_objs_dict


def collect_products(product_type: str, specific_product: str) -> list:
    if product_type != 'show_all' and product_type != 'specific_product':
        return [product for product in products_objs_dict if product['type'] == product_type]
    
    elif product_type == 'specific_product':
        for product_from_dict in products_objs_dict:
            print('from dict', product_from_dict['name'].lower())
            print('specific product', specific_product.lower())
            if (product_from_dict['name'].lower() in specific_product.lower()) or (specific_product.lower() in product_from_dict['name'].lower()):
                return [product_from_dict]
    else:
        return products_objs_dict