from sentence_transformers import SentenceTransformer
import numpy as np

# load model once when server starts
model = SentenceTransformer('all-MiniLM-L6-v2')

def improve_query(user_query: str) -> str: # function take text from usr and improve request for eBay

    #encode user query into vector -massive numbers that discribes meaning of text "whant listen to music" → [0.2, 0.8, 0.1, ...] 
    query_embedding = model.encode(user_query) 


    # list of the most whidespread categories in eBay - we will compere requests with it
    ebay_terms = [
        "laptop", "phone", "tablet", "headphones", "camera",
        "gaming", "keyboard", "monitor", "speaker", "watch"
    ]

    # encode all ebay terms  in vectors
    terms_embeddings = model.encode(ebay_terms) 

    # Compere request vector with category vector using Dot product — the more near number, the more simular meaning 
    similarities = np.dot(terms_embeddings, query_embedding)
    best_match = ebay_terms[np.argmax(similarities)]

    # If category already exist in request don't add, if not - add to request
    if best_match not in user_query.lower():
        return f"{user_query} {best_match}"
    return user_query

#async def smart_search(query: str, offset: int = 0 ): # take usr request and offset
#    from api.ebay import search_ebay # imprt here to avoid circul import

    # try ai impproved query first
#    improved_query = improve_query(query)
#    clean_query = " ".join([w for w in query.split() if len(w) > 2])
    
#    print(f"original: {query}")
#    print(f"improved: {improved_query}")
#    print(f"clean: {clean_query}")

#    if improved_query != query: # if ai changed request give item with market "ai"
#        items = await search_ebay(improved_query, offset)
#        if items:
#            return items, "👁‍🗨 aeye" # found with ai

#    # if ai couldn't help or didn't changed request - search using original request and methods with mark "normal" 
#    items = await search_ebay(clean_query, offset)
#    if items:
#        return items, "👁‍🗨 aeye"

#    items = await search_ebay(query, offset)
#    return items, "🔍 Normal"

async def smart_search(query: str, offset: int = 0):
    from api.ebay import search_ebay

    improved_query = improve_query(query)
    
    # remove common words, keep only important ones
    stop_words = {"i", "want", "need", "looking", "for", "with", "and", "the", 
                  "gigs", "color", "white", "black", "new", "old", "good", "nice",
                  "some", "please", "can", "you", "find", "get", "me", "of", "ram",
                  "gigs", "gb", "inch", "size", "big", "small"}
    
    words = [w for w in query.lower().split() if w not in stop_words and len(w) > 2]
    clean_query = " ".join(words)
    
    print(f"Original: {query}")
    print(f"Improved: {improved_query}")
    print(f"Clean: {clean_query}")

    if improved_query != query:
        items = await search_ebay(improved_query, offset)
        if items:
            return items, "👁‍🗨 Aeye"

    items = await search_ebay(clean_query, offset)
    if items:
        return items, "👁‍🗨 Aeye"

    items = await search_ebay(query, offset)
    return items, "🔍 Normal"