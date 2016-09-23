# Amazon Alexa and Twilio Powered Customer Service
Imagine a possibility where your customers can quickly request a phone callback from a customer service agent without navigating the company's website to ask for a callback or picking up a phone to dial a toll free number. 

Today, such streamlined customer journeys are easy to create when we consider augmenting the emerging world of voice assistant driven customer interactions with existing contact centre investments.  One such assistant technology is Amazon Alexa voice skills built within Amazon Echo speaker.  Alexa custom skills allow implementing voice based interactions with a customer through the Echo speaker.   Twilio provides the critical communication layer between the consumer  and your backend contact centre infrastructure.

I'll show how using Alexa custom skills and Twilio's APIs you can develop a two way conversation by collecting relevant context from the customer and then set up a phone callback.  You can connect the customer to your existing contact center (via PSTN phone number or SIP) or into your contact centre built on Twilio.

Let's get started... 

# Pre-requisites  
Amazon Echo (you can buy here: Amazon UK, Amazon US)
Knowledge of Alexa Custom Skills
Twilio Account [Sign up for a Twilio account](https://www.twilio.com/try-twilio)
Knowledge of Twilio voice API

Level: Intermediate, Advanced

# The customer journey using Amazon Echo is following:
* Customer initiates the callback service skill by saying: “Alexa ask Twilio customer callback”
* Alexa interacts and collects the context and reason for callback request from the customer
* Then, Alexa custom skills (via the AWS lambda function) invokes the Twilio server side Python SDK
* Twilio Python SDK using the Twilio REST API follows one of the three possible flows to connect to the call center:
  * For PSTN connectivity to the contact center, Twilio will dial the contact center and customer’s phone number and bridge the two party
  * For SIP connectivity to the contact center, Twilio will connect to  the contact center (PBX/SBC) over SIP 2.0 and customer’s phone number and bridge the two party
  * For connection to a Twilio based contact center, your web application  will first create a task for the agent (using TaskRouter).  When the next available agent accepts the task, Twilio will initiate a call from the agent desktop (using WebRTC) to the customer’s phone (via global carrier network) and bridge the two party

# High level Architecture:



# Architectural Components Setup:
  a) Alexa Custom Skills Configuration:
  The Alexa custom skills provides speech to text functionality, intent recognition and extraction of attributes from spoken phrases.  These instructions assume you’re familiar with developing Alexa custom skills. 

# Skill Information setup:

# Interaction Model:
  Next, we need to setup and train Alexa with our interaction model.  Your setup will look like this:
Intent Schema:


Custom Slots:

Sample Utterances:

	
Note: The source model can be found on this github repository 

  b) AWS Lambda function to interact with Alexa skills: 
The AWS lambda function works in conjunction with Alexa custom skills to provide the business logic needed for the conversation between the user and Alexa.  It also gathers the required attributes and eventually passes it to Twilio REST API to make the outbound call to the contact centre and customer.
Note: The source code for the Lambda function can be found on this github repository 

# Summary
It’s important to serve customers over newly emerging channels for better customer experience and to differentiate your brand.  Integrating Amazon Echo and Alexa Skills as newer channels into your existing contact center infrastructure is pretty easy.  Twilio provides the critical communication  glue between these consumer devices and your backend contact centre infrastructure.

I hope you found this post and code helpful.  I look forward to hearing about your use cases.

