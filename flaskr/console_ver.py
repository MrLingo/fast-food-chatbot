from difflib import SequenceMatcher
import json

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

user_input = input("Talk to Viki: ")
temp_dict = {}


with open("static/database.json") as file:
    data_dict = json.load(file)


''' Traversing data dict and filling a temporary one ( answer:ratio ). '''
for i in data_dict:
    ratio = similar(i, user_input.lower())
    temp_dict[data_dict[i]] = ratio


''' Choosing the one with the best ratio from the generated one. '''
final_answer = max(temp_dict, key=temp_dict.get)
accuracy = temp_dict[final_answer]


''' reformating the accuracy ( show in %) '''
accuracy = round(accuracy, 1)
accuracy = accuracy * 100
response_list = [final_answer, accuracy]          

''' Return Viki's response to the user! '''
print(final_answer)
print(accuracy)