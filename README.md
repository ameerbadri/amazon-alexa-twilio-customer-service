# Amazon Alexa and Twilio Powered Customer Service
Imagine a possibility where your customers can quickly request a phone callback from a customer service agent without navigating the company's website to ask for a callback or picking up a phone to dial a toll free number. 

Today, such streamlined customer journeys are easy to create when we consider augmenting the emerging world of voice assistant driven customer interactions with existing contact centre investments.  One such assistant technology is Amazon Alexa voice skills built within Amazon Echo speaker.  Alexa custom skills allow implementing voice based interactions with a customer through the Echo speaker.   Twilio provides the critical communication layer between the consumer  and your backend contact centre infrastructure.

I'll show how using Alexa custom skills and Twilio's APIs you can develop a two way conversation by collecting relevant context from the customer and then set up a phone callback.  You can connect the customer to your existing contact center (via PSTN phone number or SIP) or into your contact centre built on Twilio.

# A possible customer journey using Amazon Echo:
* Customer initiates the callback service skill by saying: “Alexa ask Twilio customer callback”
* Alexa interacts and collects the context and reason for callback request from the customer
* Then Alexa custom skills (via the AWS lambda function) invokes the Twilio server side Python SDK
* Twilio Python SDK using the Twilio REST API follows one of the three possible flows to connect to the call center:
	* For PSTN connectivity to the contact center, Twilio will dial the contact center and customer’s phone number and bridge the two party
	* For SIP connectivity to the contact center, Twilio will connect to  the contact center (PBX/SBC) over SIP 2.0 and customer’s phone number and bridge the two party
	* For connection to a [Twilio based contact center](https://github.com/nash-md/twilio-contact-center), your web application  will first create a task for the agent (using TaskRouter).  When the next available agent accepts the task, Twilio will initiate a call from the agent desktop (using WebRTC) to the customer’s phone (via global carrier network) and bridge the two party


Let's get started... 

# Pre-requisites  
Amazon Echo (you can buy here: [Amazon UK](https://www.amazon.co.uk/dp/B01GAGVIE4), [Amazon US](https://amzn.com/B00X4WHP5E))
Knowledge of Alexa Custom Skills
Twilio Account [Sign up for a Twilio account](https://www.twilio.com/try-twilio)
Knowledge of Twilio voice API

Level: Intermediate, Advanced

# High level Architecture:
![](Signal_London_2016_Building_A_Twilio_Powered_Contact_Center.001.jpeg)

![](Signal_London_2016_Building_A_Twilio_Powered_Contact_Center.001.jpeg)


# Architectural Components Setup:
  a) Alexa Custom Skills Configuration:
  The Alexa custom skills provides speech to text functionality, intent recognition and extraction of attributes from spoken phrases.  These instructions assume you’re familiar with developing Alexa custom skills. 

# Skill Information setup:
![](alexa_interaction_model_1.png)

# Interaction Model:
  Next, we need to setup and train Alexa with our interaction model.  Your setup will look like this:
Intent Schema:
![](alexa_interaction_model_2.png)

Custom Slots:
![](alexa_interaction_model_3.png)

Sample Utterances:
![](alexa_interaction_model_4.png)
	
Note: The source model can be found on this github repository 

b) AWS Lambda function to interact with Alexa skills: 
The AWS lambda function works in conjunction with Alexa custom skills to provide the business logic needed for the conversation between the user and Alexa.  It also gathers the required attributes and eventually passes it to Twilio REST API to make the outbound call to the contact centre and customer.
You’ll need to configure the following:
config.py: Replace the value for Twilio Account Sid and Auth Token with your own credentials.
![](config_setup.png)

Lambda_function.py: Replace the following values.
![](lambda_function_change_1.png)

![](lambda_function_change_2.png)

Once you have made the above changes, you’ll need to zip all the files in the “lambda function” folder.  On OS X, the system will create Archive.zip file.  You’ll upload this ZIP file to AWS as your lambda function.

Note: Makes sure you only zip the contents (files and sub-folders)  of the “lambda function” folder and not the folder itself.
The source code for the Lambda function can be found on this github repository 

Next, you’ll need to enable this custom skill in your Alexa app connected to your Amazon Echo.
Finally, invoke the Alexa customer callback skill by saying the following to your Amazon Echo:
# “Alexa open twilio customer callback”

# Summary
It’s important to serve customers over newly emerging channels for better customer experience and to differentiate your brand.  Integrating Amazon Echo and Alexa Skills as newer channels into your existing contact center infrastructure is pretty easy.  Twilio provides the critical communications glue between these consumer devices and your backend contact centre infrastructure.
I hope you found this post helpful.  I look forward to hearing about your use cases.
