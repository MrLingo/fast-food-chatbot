from openpyxl import load_workbook
from nltk import ngrams
from flaskr.knowledge_retreiver import config_dict


autocomplete_path: str = config_dict['autocomplete_memory_path']


def store_input_for_autocomplete(user_input: str) -> None:
    # If input long enough (at least three words) - build trigrams.
    words = user_input.split()
    if len(words) >= 3:
        trigrams = ngrams(words, 3)

        for trigram in trigrams:
            # Uncomment for debugging
            #print('first part ', trigram[0])
            #print('second part ', trigram[1])
            #print('third part ', trigram[2])
            print(' =================== ')

        prefix = trigram[0] + ' ' + trigram[1]
        suffix = trigram[2]
                
        write_to_excel_autocomplete(prefix, suffix)


def write_to_excel_autocomplete(prefix: str , suffix: str) -> None:
    new_row_data = [prefix, suffix]
    wb = load_workbook(autocomplete_path)
    ws = wb.worksheets[0]

    ws.append(new_row_data)
    wb.save(autocomplete_path)