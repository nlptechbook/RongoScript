<img src="https://github.com/nlptechbook/RongoScript/blob/main/Icon/moai.jpg" align="left" width="100px"/>

# RongoScript: Bot engine with transformer
<sub>Art by Konstantin Lupanov</sub> 
<br clear="left"/>

RongoScript is a software product designed to be used as a bot engine that relies on natural language to communicate with the user. The concept is similar to that one used in Google's DialogFlow: the system processes and categorizes user input, reacting in a predefined way. 

To classify user input, RongoScript encapsulates a neural network with a transformer architecture. A simplified version of the engine is used in our @RongoScriptBot demo bot in Telegram. The bot allows you to test the engine on your own data or use a provided set. More about this below in the Demo bot in Telegram section.

The following sections give a brief overview of the technologies encompassed by RongoScript
## Classifying user phrases with a transformer 
The idea is that the bot receives an utterance from the user in natural language and classifies it to a certain intent, in order to execute the assigned command or generate an adequate response. To solve the classification problem, RongoScript uses the neural network based on a transformer. When an intent is identified, the action assigned to it is performed. For example, a predefined function is executed with the parameters passed in, which are retrieved from the user's utterance; or - in the simplest case - a hardcoded response is sent back.  
## Processing text data before feeding it to the transformer
Before utterances are fed into the transformer (both during training and during classification), they are pre-processed. The next sections describe the main steps of this pre-processing. The code for the operations described here can be found in the [preprocessing](https://github.com/nlptechbook/RongoScript/tree/main/preprocessing) folder of this repository.
### Lemmatization
Lemmatization is the process of reducing different forms of a word (token) to their lemma. The lemma is the basic form of the word. For clarity, a lemma can be thought of as the form in which a word appears in a dictionary. For example, the lemma for "does" is "do". The most important thing about lemmatization is that it reduces the number of unique words found in the training phrases and, therefore, it reduces the volume of the vocabulary required for acceptable operation of the classifier.
### NER processing 
NER (named entity recognition) processing is performed in two stages. First, the named entities found in the text (names of people, organizations, cities, dates, etc.) are stored in a dictionary, which can then be sent to the function defined for this class((if any).
The next step involves replacing the named entities with their corresponding labels. So, for example, Paris will be replaced by GPE, and, say, DeepPavlov by ORG. This contributes to the generalization of the data, thus improving the predictive accuracy of the classifier. 

For example, the phrases:
> What will the weather be like in London tomorrow?

and 
>What will the weather be like the day after tomorrow in LA?

will be reduced to the same single phrase: 
>What will the weather be like in DATE in GPE?

Thus, allowing the classifier to uniquely identify all such phrases. At the same time, as noted above, the previously extracted specific names can be passed to processing to generate a response specific to this particular request. 

### Syntactic dependency analysis
Sometimes, submitted utterances need to be processed through more than just lemmatization and NER processing touched upon in the above sections. For example, in the utterance:

>I wonder how computers understand language.

You may need to pass only the complement clause to the classifier: 

>how computers understand language

While the predicate 'wonder' should also be taken into account as the embedding predicate needed to determine how much the user is committed to the assertion in the complement clause. In simple terms, you need to perform a more complicated, "smart" processing of the input. 

> **Note**: To gain a cursory understanding of the underlying theory, you might explore the [CommitmentBank Dataset](https://metatext.io/datasets/commitmentbank), a resource for studying projection behavior of finite clausal complements in naturally occurring data.

RongoScript allows you to take advantage of this functionality by passing additional parameters to the get_response() method of the model. An example of such a call can be found in the Using RongoScript in code section later. To understand where this capability can be applicable, consider the following example:

Suppose you want to learn what people think about why [rongorongo](https://en.wikipedia.org/wiki/Rongorongo) - a system of mysterious glyphs discovered on the island of Rapa Nui - still has not been deciphered. To address this task, you might create a bot that asks its users the following question:

>Why do you think rongorongo has not been deciphered yet? 

You could have trained the underlying model to classify users answers into just these two categories:

>1. That's a technical issue: researchers are to develop an algorithm that will lead to a successful solution.
>2. The problem is that we know almost nothing about those who used the script: the context is important.

Now suppose the bot receives the following utterance (referred to as a premise, in the terms of CommitmentBank): 

>I don't believe that the context is important. Modern researchers can employ AI and the computational power of supercomputers to successfully decipher unknown texts, regardless of whether the context is known or not. 

With the help of the "smart" processing discussed earlier in this section, the above utterance can be converted to the following one before being sent to the classifier:  

>The context is not important. Modern researchers can employ AI and the computational power of supercomputers to successfully decipher unknown texts, regardless of whether the context is known.  

This will be classified to a specific category (the first one, in this particular example), thus allowing your bot to ask a suitable follow-up question.

## Embedding based on syntactic relations instead of positional embedding 
In RongoScript, we experiment with technology. So along with the familiar positional embedding in the transformer model, we use embedding based on syntactic relations in an utterance. In this case, the words are numbered based on the level at which they are located in the tree of syntactic dependencies of the sentence. So, the main verb will be at the top level in the syntax tree. One level down in a typical sentence are such parts of speech as the subject and direct object. That is, the most significant words of the sentence will be at higher levels of the syntactic dependency tree, providing a kind of sorting of words according to their importance.

As an example, consider the following utterance:

>As a matter of fact, the server maintains a release repository.

As you can see, the utterance starts with a phrase commonly used to emphasize the truth of an assertion. From the standpoint of the conveyed meaning, however, the assertion itself matters much more. That means that in case of the positional approach the rank values for the less important words will be higher than the rank values for the more important words. While the approach based on syntactic relations will rank the words more appropriately.

## Using Pre-trained Word Embeddings in an Embedding Layer

The same thoughts can be expressed in different ways, with different, synonym words. Your text classificator should recognize such phrases, and using pre-trained word embeddings is one of those techniques that can significantly improve this ability of the classificator.  In the [Pre-trained Word Embeddings in an Embedding Layer](https://github.com/nlptechbook/PretrainedEmbeddings) repository, you'll find how this can be implemented in a transformer.  

## Taking the context of a discourse into account
Another idea we're working on is teaching the transformer to make interpretations based on not only a single phrase but also on the context of the entire discourse, so that the transformer can "understand" the meaning of a phrase issued in different contexts. 

While a discourse elaborates its context, the context helps clarify the meaning of phrases in the discourse. Sometimes, you can't understand the exact meaning of the utterance without the context of the discourse. Take the following utterance as an example:
>I want a red one. 

It doesn't make much sense without the context elaborated so far. The previous utterance of the discourse might help. For example, it could be as follows:  
>Which apple do you want?

As you can see, the most important word in this previous utterance - from the standpoint of understanding the meaning carried in the next utterance - is apple. So, we don't need to pass in the entire previous utterance: a single word extracted from it is enough. You may womder how to identify this single word (or a group of the most important words in the utterance)? The short answer is with the help of syntactic dependency analysis. 
## Demo bot in Telegram 
By this point, you might have a question: where can I see how it all works? To address this, we have created a @RongoScriptBot demo bot in Telegram that relies on RongoScript. This simple demo bot consists of the following components:
- An interface to interact with a user via text messages in Telegram
- A Transformer-based neural network for classifying user messages
- A system for processing classified user messages, which generates responses

Before the bot can start answering your questions, you need to configure the underlying RongoScript. To do this, you need to take these two actions: firstly, train the transformer neural network on specific question/answer pairs and, secondly, configure the response generation system for this specific data. Both tasks are solved by one single action of yours: running the /train_faq command (if you want to use the training set in our [faq_en.json]( https://github.com/nlptechbook/RongoScript/blob/main/faq_en.json), or uploading your json file with your data (as a Document in Telegram), but always with the same structure as our faq_en.json.

In both cases, the code will process each entry in the json file and create the appropriate training pairs. For each record in the file, one or more training pairs can be generated, according to the number of utterances in the utterance field of the record. The process of training the neural network starts automatically next. Once the message Done! is received, you can start testing the bot by entering questions from the training set used (not necessarily word for word).

If you examine our faq_en.json file, you will find an entry with the action field set to a specific value, namely get_news. This is the name of the function that will be executed if a user asks for news about a well-known company. Since the action field in this entry is set to true, the named entity (a company name is expected) will also be retrieved from the utterance. We have included this as an example of an entry with a handler implemented as a function that generates a dynamic response.

Thus, to the utterance: "What's new about Tesla?" we've got the following response in May 21: 

> 2022-05-16T20:53:25Z  
> Tesla's long-delayed Semi just took an important step toward becoming a practical reality. As CNETreports, the automaker has started taking reservations for its electric big rig. You'll need to place a $20,000 deposit ($15,000 of it by wire transfer), and Tes…
https://www.engadget.com/tesla-semi-electric-big-rig-reservations-205325433.html

> 2022-05-08T15:05:10Z  
> Tesla has sued a former employee who it is accusing of stealing trade secrets related to its supercomputer project, Bloomberg reported on Friday. According to a filing in the U.S. District Court in San Jose, thermal engineer Alexander Yatskov quit on May 2 af…
https://www.engadget.com/tesla-sues-engineer-dojo-trade-secret-theft-150510141.html

> 2022-05-10T17:37:13Z  
> Future Twitter owner and Tesla billionaire Elon Musk appeared in a video with EU Commissioner Thierry Breton to reiterate his support for the Digital Services Act.
https://www.theverge.com/2022/5/10/23065270/elon-musk-twitter-digital-services-act-dsa-european-union-eu-speech-laws-thierry-breton  

In production, you could define much more classes with a handler function, of course.

> **Warning**
> The bot may work intermittently since we do not have a dedicated server for it. If it doesn't work right now, please try again later. 
## Using RongoScript in code
Here is a quick example of using RongoScript in code. We provide it just to give you an idea of how RongoScript wrapped into a Python library can be used in development. (Please note that the rongoscript library shown here is not publicly avalable at the moment.) 
```python
#Creating and training a model on data found in a json file  
import rongoscript as rs   
pathtojson ='/path/to/training/data/file'  
model = rs.create_model(training_data = pathtojson, lang = 'en')

# Using the model for getting appropriate responses to user's phrases
phrase = 'This is a user phrase.'
response = model.get_response(phrase)  

# Invoking get_response() with additional parameters for "smart" processing 
phrase = 'I know this user phrase has a complement clause.'
response = model.get_response(phrase, preprocessing = 'smart', type = 'cc') 

# Saving the model to disk   
model.save('/path/to/location')

# Loading it back into a variable
model = rs.load_model('path/to/location')

```
 An example of the usage of rongoscript in a Telegram bot can be found in /Bot/rongobot.py of this repository.
