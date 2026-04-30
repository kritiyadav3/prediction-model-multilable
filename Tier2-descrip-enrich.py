from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
import pandas as pd

# For each tag, find the top-15 most discriminative words
# from complaints that carry that tag

def extract_tag_keywords(df_tr, y_tr, valid_tags, top_n=15):
    tag_keywords = {}
    
    for i, tag in enumerate(valid_tags):
        # Get all summaries where this tag is present
        mask = y_tr[:, i] == 1
        tag_summaries = df_tr.loc[mask, 'summary'].fillna('').tolist()
        
        if len(tag_summaries) < 3:
            tag_keywords[tag] = []
            continue
        
        # TF-IDF on just this tag's complaints
        tfidf = TfidfVectorizer(
            max_features=500,
            ngram_range=(1, 2),
            sublinear_tf=True,
            stop_words='english'
        )
        try:
            tfidf.fit(tag_summaries)
            # Get top words by mean TF-IDF score
            scores = np.array(tfidf.transform(tag_summaries).mean(axis=0)).flatten()
            top_idx = scores.argsort()[-top_n:][::-1]
            top_words = [tfidf.get_feature_names_out()[j] for j in top_idx]
            tag_keywords[tag] = top_words
        except:
            tag_keywords[tag] = []
    
    return tag_keywords

tag_keywords = extract_tag_keywords(df_tr, y_tr, valid_tags, top_n=15)

# Preview
for tag, kws in list(tag_keywords.items())[:5]:
    print(f"\n{tag}:")
    print(f"  Keywords: {', '.join(kws)}")
