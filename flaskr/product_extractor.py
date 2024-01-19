from openpyxl import load_workbook
from flaskr.knowledge_retreiver import config_dict


extracted_products_path : str = config_dict['extracted_products_path']

def extract_products(topic_words : list, products_dict : dict, topic_type : str) -> list:
    recommended_topics_list = []

    for topic_word in topic_words:    
        for key in products_dict:
            if topic_type == "NN" and topic_word[0] in key:
                recommended_topics_list.append(topic_word[0])
            elif topic_type == "LDA" and topic_word in key:
                recommended_topics_list.append(topic_word)

    return recommended_topics_list


def store_extracted_products(extracted_products : list) -> None:
    # To store every item from the list in one cell
    new_row_data = extracted_products
    wb = load_workbook(extracted_products_path)

    ws = wb.worksheets[0]

    print('new row: ', new_row_data)
    ws.append(new_row_data)
    wb.save(extracted_products_path)