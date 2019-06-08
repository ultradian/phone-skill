# phone-skill
Alexa skill demonstrating DynamoDB persistence

to make this work on AWS Lambda, create a folder like `src` which contains the `ask-sdk` libraries and the file [lambda_function.py](lambda_function.py) and zip it together and upload.

if you want to build your own `src` folder with the latest libraries, you would execute the command:
```
pip install ask-sdk -t src/
```
to download them all from pypI

to get it functioning, you would also need to install the interaction model on the Alexa service
* [model.json](model.json/) - interaction model for skill
