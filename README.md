## Running the N-gram Viewer 
Navigate to the Web folder to launch the Flask application (`python ngram.py`). 

In addition to Flask, this project requires nltk. After installing nltk, make sure to download the vader_lexicon.txt data file. The download GUI is available via:

```python
import nltk
nltk.download()
```

In the GUI, navigate to the "All Packages" tab and search for the identifier "vader_lexicon". Confirm data download by running:

```python
from nltk.sentiment.vader import SentimentIntensityAnalyzer
sid = SentimentIntensityAnalyzer()
```

## Notes
The "IW Presentation" folder contains a slide deck explaining the project.

My final research paper for this project can be found [here](https://github.com/dliu18/papers/blob/master/digital_humanities.pdf).
