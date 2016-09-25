"""
This sample demonstrates a new channel of customer service via Amazon Alexa Skills.
This demo shows a conversation between a customer and an intelligent agent (IA) Alexa via Amazon Echo
to collect information and setup a customer service callback.  This new channel is an augmentation to the
traditional channels such as calling an IVR or customer callback contact form on a company website.

Using Twilio the customer can be connected to the following types of call centers:
a) Twilio powered modern contact center
b) A traditional call center by dialing a phone number via PSTN
c) A traditional call center by connecting to a PBX/SBC via SIP

For additional samples about using Alexa Skills, visit the Getting Started guide at
http://amzn.to/1LGWsLG

Ameer Badri
Twilio
"""

from __future__ import print_function
# import pytz
import sys
import requests
import config
import json
import urllib
import re

from twilio import twiml, TwilioRestException
from twilio.rest import TwilioRestClient

session_attributes = {}

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])
    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    #if (event['session']['application']['applicationId'] != "<YOUR_APPLICATON_ID>"):
    #    raise ValueError("Invalid Application ID")
    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])

def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])

def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """
    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # lets call the intent processing directly
    intent = {"name": "CustomerServiceIntent"}
    return customer_callback_service(intent, session)
    # Dispatch to your skill's launch
    # return get_welcome_response()

def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "CustomerServiceIntent":
        return customer_callback_service(intent, session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")

def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here

# --------------- Functions that control the skill's behavior ------------------
def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """
    card_title = "Twilio Customer Service"
    speech_output = "Welcome to Twillio Customer Service. " \
            " This channel is powered by Amazon Alexa Skills. You can start by saying, Alexa open Twilio customer callback"
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "Welcome to Twillio Customer Service. " \
            " This channel is powered by Amazon Alexa Skills. You can start by saying, Alexa open Twilio customer callback"
    should_end_session = True
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Thank you for using Twillio Customer Service. " \
                    "Have a nice day! "
    reprompt_text = "Thank you for using Twillio Customer Service. " \
                    "Have a nice day! "
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

# List of account names and additional details
# Replace name and phone numbers
accounts = {
    "ameer": [{"phonenumber": "+447477121234",
                "supportlevel": "Premium"}],
    "simon": [{"phonenumber": "+14155081234",
                "supportlevel": "Bronze"}]
}

def lookup_customer_account(name):
    account = {}
    account_name = name.lower()
    print('Looking up Account Name: ' + account_name)
    try:
        account = accounts[account_name]
        account = account[0]
    except:
        account = {}
    print ('Account info: ' + json.dumps(account))
    return (account)

def customer_callback_service(intent, session):
    """ Sets the name to be called in the session and prepares the speech to reply to the
    user.
    """
    card_title = intent['name']
    should_end_session = False
    speech_output = ""
    reprompt_text = ""
    print ('Intent: ' + str(intent))
    print ('Session: ' + str(session))
    if 'False' in str(session['new']):
        if 'get_customername' in session_attributes['callback_flow']:
            if 'customername' in intent['slots']:
                if 'value' in intent['slots']['customername']:
                    # This is a conversation about customer name
                    customername = intent['slots']['customername']['value']
                    session_attributes['customername'] = customername
                    print ('Looking up account details')
                    account_details = {}
                    account_details = lookup_customer_account(customername)
                    print ('Account details: ' + account_details['phonenumber'])
                    session_attributes['customer_phonenumber'] = account_details['phonenumber']
                    session_attributes['customer_supportlevel'] = account_details['supportlevel']
                    # We didn't find a callback phone number in our DB.  Lets collect it first.
                    if not session_attributes['customer_phonenumber']:
                        session_attributes['callback_flow'] = 'get_phone_number';
                        print ('Session Attributes: ' + str(session_attributes))
                        speech_output = session_attributes['customername'] + ", I did not find a phone number for the callback in the system . Let me get your phone number. " \
                            "Please say your phone number starting with country code."
                        reprompt_output = session_attributes['customername'] + ", I did not find a phone number for the callback in the system. Let me get your phone number. " \
                            "Please say your phone number starting with country code."
                    else:
                        session_attributes['callback_flow'] = 'get_department'
                        print ('Session Attributes: ' + str(session_attributes))
                        speech_output = session_attributes['customername'] + ", I was able to lookup your phone number and account details in the system. " \
                                "Which department would you like to contact?  Sales, Marketing or Support"
                        reprompt_text = session_attributes['customername'] + ", I was able to lookup your phone number and account details in the system. " \
                                "Which department would you like to contact?  Sales, Marketing or Support"
                else:
                    speech_output = "What is the account name?"
                    reprompt_text = "Please say the account name."
        elif 'get_phone_number' in session_attributes['callback_flow']:
            if 'phonenumber' in intent['slots']:
                if 'value' in intent['slots']['phonenumber']:
                    # This is a conversation about collecting phone number
                    phonenumber = intent['slots']['phonenumber']['value']
                    phonenumber = '+' + re.sub(r'\D', "", phonenumber)
                    session_attributes['customer_phonenumber'] = phonenumber
                    session_attributes['callback_flow'] = 'get_department'
                    print ('Session Attributes: ' + str(session_attributes))
                    speech_output = "Which department would you like to contact?  Sales, Marketing or Support"
                    reprompt_text = "Which department would you like to contact?  Sales, Marketing or Support"
                else:
                    speech_output = "Which department you would like to contact?  Sales, Marketing or Support"
                    reprompt_text = "You can say. Sales, Marketing or Support"
        elif 'get_department' in session_attributes['callback_flow']:
            if 'department' in intent['slots']:
                if 'value' in intent['slots']['department']:
                    # This is a conversation about department
                    departmentname = intent['slots']['department']['value']
                    session_attributes['departmentname'] = departmentname.lower()
                    session_attributes['callback_flow'] = 'get_reason'
                    print ('Session Attributes: ' + str(session_attributes))
                    speech_output = "Briefly describe the reason for your inquiry."
                    reprompt_text = "Briefly describe the reason for your inquiry."
                else:
                    speech_output = "Which department you would like to contact?  Sales, Marketing or Support."
                    reprompt_text = "You can say, Sales, Marketing or Support."
        elif 'get_reason' in session_attributes['callback_flow']:
            if 'reason' in intent['slots']:
                if 'value' in intent['slots']['reason']:
                    # This is a conversation about callback reason
                    reason = intent['slots']['reason']['value']
                    session_attributes['reason'] = reason
                    session_attributes['callback_flow'] = 'get_callback_confirmation'
                    print ('Session Attributes: ' + str(session_attributes))
                    collected_info = 'Here is the summary of your request.  Account Name  ' + session_attributes['customername']
                    # collected_info = collected_info + '. Contact phone number <say-as interpret-as="telephone">' + session_attributes['customer_phonenumber'] + '</say-as>'
                    collected_info = collected_info + '. Support Level, ' + session_attributes['customer_supportlevel']
                    collected_info = collected_info + '. Department to contact, ' + session_attributes['departmentname']
                    collected_info = collected_info + '. Reason for callback,  ' + session_attributes['reason']
                    speech_output = collected_info + ". Would you like to proceed?  Say yes or no."
                    reprompt_text = " . Would you like to proceed?  Say yes or no."
                    should_end_session = False
        elif 'get_callback_confirmation' in session_attributes['callback_flow']:
            if 'confirm' in intent['slots']:
                if 'value' in intent['slots']['confirm']:
                    if intent['slots']['confirm']['value'].lower() in ['yes', 'yep']:
                        augmentation_type = session_attributes['augmentation_type']
                        if augmentation_type == 'twilio_contact_center':
                            #
                            # Augmentation Type: 1
                            # Call the Task creation API in Twilio Contact Center Demo app
                            #
                            task = {
                                'channel': 'phone',
                                'phone': session_attributes['customer_phonenumber'],
                                'name': session_attributes['customername'],
                                'supportlevel': session_attributes['customer_supportlevel'],
                                'text': 'Support Level - ' + session_attributes['customer_supportlevel'] + ': ' + session_attributes['reason'],
                                'team': session_attributes['departmentname'],
                                'type': 'Callback request'
                            }
                            # Create a taskrouter task in contact center for a callback (separate contact center demo install required)
                            # Change the domain name below to your install of the contact center demo
                            # For details see: https://github.com/nash-md/twilio-contact-center
                            r = requests.post('<yout_twilio_contact_center_demo>.herokuapp.com/api/tasks/callback', data = task)
                        elif augmentation_type == 'pstn':
                            #
                            # Augmentation Type: 2
                            # Call existing contact center over PSTN
                            #
                            # Replace the value with your call center agent phone number.  E.164 format
                            agent_phone_number = "+14151234567"
                            say_language = config.LANGUAGE
                            resp_customer = twiml.Response()
                            resp_customer.pause()
                            resp_customer.say("Hello, " + session_attributes['customername'], voice="alice", language=say_language)
                            resp_customer.say("This is a callback from Twilio support. Connecting you to an agent.", voice="alice", language=say_language)
                            # Create the URL that Twilio will request after the customer is called
                            # Use the echo Twimlet to return TwiML that Twilio needs for the call
                            customer_url = "http://twimlets.com/echo?Twiml=" + urllib.quote_plus(str(resp_customer))
                            print("customer url: " + customer_url)
                            # Create Twiml that will be played to the call center agent when the call is answered
                            resp_agent = twiml.Response()
                            resp_agent.pause()
                            resp_agent.say("Customer " + session_attributes['customername'] + ", Is requesting a callback.", voice="alice", language=say_language)
                            resp_agent.say(",Reason for their inquiry, " + session_attributes['reason'], voice="alice", language=say_language)
                            resp_agent.say(",Dialing the customer ", voice="alice", language=say_language)
                            with resp_agent.dial(callerId = agent_phone_number) as r:
                                r.number(session_attributes['customer_phonenumber'], url=customer_url)
                            # Create the URL that Twilio will request after the agent is called
                            # Use the echo Twimlet to return TwiML that Twilio needs for the call
                            agent_url = "http://twimlets.com/echo?Twiml=" + urllib.quote_plus(str(resp_agent))
                            print("agent url: " + agent_url)
                            # Make an outbound call to the agent first and then dial the customer
                            # Replace the "to" with your contact center agent's phone number
                            client = TwilioRestClient(config.ACCOUNT_SID, config.AUTH_TOKEN)
                            call = client.calls.create(
	                           to=agent_phone_number,
	                           from_=session_attributes['customer_phonenumber'],
	                           url=agent_url)
                        elif augmentation_type == 'sip':
                            #
                            # Augmentation Type: 3
                            # Call existing contact center over SIP
                            #
                            resp = twiml.Response()
                            resp.say("Hello, " + session_attributes['customername'])
                            resp.say("This is a callback from Twilio support. Connecting you to an agent.")
                            # Insert your company contact center SIP address
                            with resp.dial() as r:
                                r.sip("sip_name@company.com")
                            resp_string = urllib.urlencode(str(resp))

                        session_attributes['callback_flow'] = 'callback_request_complete'
                        speech_output = "OK. I will pass this information to the next available agent. You will receive a call shortly."
                        reprompt_text = ""
                        # this will end the customer support request session
                        should_end_session = True
                    else:
                        speech_output = "Your request has been cancelled.  Have a great day!"
                        reprompt_text = ""
                        # this will end the customer support request session
                        should_end_session = True
        else:
            speech_output = "Please re-try requesting customer service"
            reprompt_text = ""
            should_end_session = True
    # Invoked at the very first instance of this customer callback flow
    else:
        # initialize configuration
        # Callback_flow acts as a state machine that allows the creation of a
        # structured conversation between the user and alexa.
        session_attributes['callback_flow'] = 'get_customername'
        # Augmentation_type is set to invoke one of the three options for
        # connecting into the backend call center
        # pstn: Dialing an agents phone number directly
        # sip: connecting to a PBX or SBC
        # twilio_contact_center: creating a callback task into the twilio contact center demo app
        session_attributes['augmentation_type'] = 'pstn'
        greeting_message = 'Hello!'
        speech_output = greeting_message + " Welcome to Twillio Customer Service. " \
            "First, I will collect some information, and then setup a " \
            "callback from a customer service agent.  Lets get started!  What is the account name? "
        reprompt_text = "Welcome to Twillio Customer Service. Lets get started.  What is the account name? "

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

#
# --------------- Helpers that build all of the responses ----------------------
#

def build_speechlet_response_plaintext(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': 'SessionSpeechlet - ' + title,
            'content': 'SessionSpeechlet - ' + output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'SSML',
            'ssml': '<speak>' + output + '</speak>'
        },
        'card': {
            'type': 'Simple',
            'title': 'SessionSpeechlet - ' + title,
            'content': 'SessionSpeechlet - ' + output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'SSML',
                'ssml': '<speak>' + reprompt_text + '</speak>'
            }
        },
        'shouldEndSession': should_end_session
    }

def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }
