from nltk import word_tokenize, pos_tag
from nltk.corpus import stopwords


def nouns_extraction(text: str) -> tuple[list, str]:
    tokens = word_tokenize(text)
    stopwords_removed = stopwords.words('english')
    no_stopwords_text = [t for t in tokens if t not in stopwords_removed]
    pos_tags = pos_tag(no_stopwords_text)

    topics = [tag for tag in pos_tags if tag[1] == 'NN']
    print('NN Topics: ', topics)
    return topics, 'NN'