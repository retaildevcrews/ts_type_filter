from nltk.stem.snowball import SnowballStemmer
import re

def nop_extractor(document):
  """
  In some cases a document may just be a string of its text content.
  In other cases it may be a more complex object containing metadata.
  The extractor gets the text content out of the document.

  This default implementation just returns the document itself.

  Note that the return type is list of string, because some documents
  may have multiple streams of text (e.g. title, body, etc.)
  """
  return [document]

def break_on_whitespace(text):
  """
  Very simple word-breaker that breaks the text into words based on whitespace.
  A more sophisticated implementation would probably break on punctuation as well.

  Note that the breaker API would need to be modified to support highlighting.
  """
  return text.strip().split()

class Index:
  def __init__(self, extractor=None, breaker=None, stemmer=None):
    self._extractor = extractor or nop_extractor
    self._breaker = breaker or break_on_whitespace
    self._stemmer = stemmer or SnowballStemmer("english")

    # Initialize the index data structures
    self._documents_in_order = []
    self._documents = set()
    self._postings = {}
    

  def add(self, document):
    if document in self._documents:
      raise ValueError("Attempting to add duplicate document.")

    # Add the document to the index
    self._documents_in_order.append(document)
    self._documents.add(document)

    # Update the postings list
    streams = self._extractor(document)
    words = []
    for text in streams:
      words.extend(self._breaker(text))
    stemmed = {self._stemmer.stem(word) for word in words}
    for word in stemmed:
      if word not in self._postings:
        self._postings[word] = []
      self._postings[word].append(document)

  def match(self, query):
    """
    Matches the given disjunctive query against the indexed documents
    and returns a list of matching documents. The documents are in the
    order they were added to the index.

    Args:
      query (str): The search query string. Consists of a sequence of
      words separated by whitespace. A document is considered a match
      if it contains a stemmed version of at least one of the words in
      the query.

    Returns:
      list: A list of documents that match the query.
    """
    words = self._breaker(query)
    stemmed = {self._stemmer.stem(word) for word in words}

    matches = set()
    for word in stemmed:
      if word in self._postings:
        matches.update(self._postings[word])

    # Filter ordered document list to only include matches
    results = [doc for doc in self._documents_in_order if doc in matches]
    return results
  
  def highlight(self, query, document):
    """
    Highlights the words in the document text that match the stemmed words
    from the query.

    Args:
      query (str): The search query containing words to be highlighted.
      document (str): The document in which to highlight the matching words.

    Returns:
      str: The document with matching words highlighted in bold green.

    NOTE that this niave implementation assumes a whitespace-based word-breaker.
    """
    words = self._breaker(query)
    stemmed = {self._stemmer.stem(word) for word in words}

    parts = re.split(r'(\s+)', self._extractor(document))
    highlighted = []
    for part in parts:
      if not part.isspace() and self._stemmer.stem(part) in stemmed:
        highlighted.append(f"[bold green]{part}[/bold green]")
      else:
        highlighted.append(part)
    return ''.join(highlighted)
  
  def statistics(self):
    """
    Prints statistics about the index, including the number of documents,
    the number of unique words, and the number of postings.

    Returns:
      None
    """
    num_documents = len(self._documents)
    num_unique_words = len(self._postings)
    num_postings = sum(len(postings) for postings in self._postings.values())

    print(f"Number of documents: {num_documents}")
    print(f"Number of unique words: {num_unique_words}")
    print(f"Number of postings: {num_postings}")
    print()

    word_frequencies = {word: len(postings) for word, postings in self._postings.items()}
    sorted_word_frequencies = sorted(word_frequencies.items(), key=lambda item: item[1], reverse=True)

    print("Word Frequency Table:")
    for word, frequency in sorted_word_frequencies:
      print(f"{word}: {frequency}")
  