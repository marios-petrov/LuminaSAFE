# LuminaSAFE


Application Description

Every year elder fraud increases by roughly 50%. Our application aims to combat this rise by providing a service which utilizes artificial intelligence
to guide individuals through sketchy offers and potential scams. 

Necessary Packages

- streamlit
- sqlite3
- re
- matplotlib
- numpy
- datetime
- nltk
- collections
- wordcloud
- openai
- transformers (HuggingFace)
- flask
- twillio

How to Use

1. If you're ever in a situation where you want to know whether or not you've been scammed, simply call or text "PHONE NUMBER" to speak with Lumina, or send a picture of that fishy letter to lumina via text.

2. Once you've connected with LuminaSAFE, explain your situation to Lumina and keep engaging in the dialogue with Lumina until your potential scam is illuminated.


Running your own LuminaSAFE

1. Install all of the necessary libraries and modules.

2. Input all of your API auth keys into the modules where the word "SAMPLE" is present.

3. Run your ngrok server, and make sure that your twillio url is properly configured to match your ngrok url.

4. Run the streamlitController to view the full dashboard and monitor conversations/app usage.

5. Spread your LuminaSAFE phone number to those who may need it :)


Testing

Once you have the application up and running, you can test each file uplod function/widget for the two different modes (Summarizer,Text Processor) with the provided test document. The document can be found in the repository, and it's titled "TEST_DOCUMENT". The RawText input functions/widgets can be tested by just copy and pasting the text contents of the provided document. Lastly the "wikiURL" input type can simply be tested by providing a valid Wikipedia link.
