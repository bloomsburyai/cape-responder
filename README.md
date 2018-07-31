# Responder 
Responder library

##Settings
To enable parallelization set the env variable ENABLE_PARALLELIZATION=True

### ResponderConfiguration Object
* `machine_reader_model`: the machine reading model to use. Currently `biattflow` 
* `threshold_reader`: the threshold for the machine reader
* `threshold_answer_in_document`: the threshold for the classifier predicting whether the answer is in the document
* `top_k`: the number of answers to return per question. Default 1.

### Responder Object
The Responder object should be initialised with a MachineReader configuration object as follows:

```
from machine_reader.machine_reader_core import MachineReader, MachineReaderConfiguration
machine_reader = MachineReader(configuration = MachineReaderConfiguration())
```

### Main Usage
The main usage is through the `respond` function which takes as inputs:
* list of `Document` objects, where each `Document` has:
    * `id`: string - id
    * `text`: string - representation of the document text
    * `origin`: string - representation of the document origin
* `question`: string - representation of the question

The outputs are:
* iterable of `Answer` objects where each `Answer` has:
    * `text`: string - representation of the answer text
    * `score_reader`: float - the confidence of the machine reading model
    * `score_answer_in_document`: float - the confidence of the classifier which determines whether the answer is in a given document based on the last layer of the BiAttFlow model
    * `document`: Document object of the document containing the answer
    * `span`: Tuple - index 0 is the span start and index 1 is the span end


###### Example:
```
documents = ['Context 1', 'Context 2']
question = 'Is this my question?'
documents = [Document(text=document) for document in documents]
answer = next(machine_reader.respond(documents, question))
```
