def recommend(topic_words : list, products : dict) -> list:
    recommended_topics_list = []

    for topic_word in topic_words:
        if topic_word in products:
            recommended_topics_list.append(topic_word)

    #print('recommended list:', recommended_topics_list)
    return recommended_topics_list