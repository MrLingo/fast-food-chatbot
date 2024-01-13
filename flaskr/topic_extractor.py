from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from nltk import word_tokenize, pos_tag
from nltk.corpus import stopwords

def lda_extraction(sentence, num_topics=1):  # Returns ['', '']
    # Create a document-term matrix
    vectorizer = CountVectorizer(stop_words='english')
    dtm = vectorizer.fit_transform([sentence])

    # Perform Latent Dirichlet Allocation
    lda = LatentDirichletAllocation(n_components=num_topics, random_state=42)
    lda.fit(dtm)

    # Get the most important words for each topic
    topic_words = [vectorizer.get_feature_names_out()[i] for i in lda.components_[0].argsort()[-5:][::-1]]
    print('LDA Topics: ', topic_words)
    return topic_words, 'LDA'

def nouns_extraction(text):                      # Returns [('fdfd', NN), ('fdf', NN)]
    tokens = word_tokenize(text)
    stopwords_removed = stopwords.words("english")
    no_stopwords_text = [t for t in tokens if t not in stopwords_removed]
    pos_tags = pos_tag(no_stopwords_text)

    topics = [tag for tag in pos_tags if tag[1] == "NN"]
    print('NN Topics: ', topics)
    return topics, 'NN'


# Extract topic with different methods, depending on how long the input is.
# The longer the input the more relevant LDA becomes.
def extract_topic(user_input, num_topics=1):
    if len(user_input) <= 100:
        return nouns_extraction(user_input)
    return lda_extraction(user_input)