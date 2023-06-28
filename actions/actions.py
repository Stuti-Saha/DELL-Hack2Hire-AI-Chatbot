# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions

# docker run -p 8000:8000 rasa/duckling

# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
import nltk
from nltk.tokenize import word_tokenize
nltk.download('punkt')
import re
import requests


# USER ID FORM ACTIVE


class ActionCheckUserId(Action):
    
    def name(self) -> Text:
        return "user_id_form"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        required_slots = ["user_id"]
        
        for slot_name in required_slots:
            if tracker.slots.get(slot_name) is None:
                return[SlotSet("requested_slot", slot_name)]
        
            
        return[SlotSet("requested_slot", None)]

# USER ID FORM SUBMIT


class ActionSubmitUserId(Action):
    
    def name(self) -> Text:
        return "action_submit_user_id"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        user_id = tracker.get_slot("user_id")

        words = nltk.word_tokenize(user_id)

        clean_user_id = "null"
        regex = re.compile('[a-z]*[A-Z]*[0-9]+')

        for word in words:
            if re.match(regex, word):
                clean_user_id = word

        user_id = clean_user_id
        print(f"user_id = {user_id}")

        result1 = requests.get(f"https://dell-backend.herokuapp.com/user/{user_id}")
        result2 = result1.json()


        if(result1.status_code==404):
            dispatcher.utter_message("You have entered the wrong userid. Do you want to re-enter it?")    
            return[SlotSet("user_id",None)]
        elif(result1.status_code==200):
            if(result2["role"]=="user"):
                dispatcher.utter_message(response="utter_ask_help_user")
                return[SlotSet("user_id",user_id)]

            else:
                dispatcher.utter_message(response="utter_ask_help_admin")
        
        return[]

# CHECK ORDER STATUS


class ActionCheckOrderStatus(Action):

    def name(self) -> Text:
        return "action_check_order_status"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        order_id = tracker.get_slot("order_id")
        print(f"order id = {order_id}")

        user_id = tracker.get_slot("user_id")
        
        if not order_id:
            msg = "Please enter valid order_id"
            dispatcher.utter_message(text=msg)

        if not user_id:
            msg = "You are not looged in. Please enter your userd id first"
            dispatcher.utter_message(text=msg)
            return[]

        result = requests.get(f"https://dell-backend.herokuapp.com/checkOrderStatus/{order_id}").json()
        print(type(result))
        print(result)
        error_code = result['code']
        print(error_code)
        message = ""
        error_name = ""
        if(error_code == '0'):
            message = "Your Order is successfull."
            error_name = "null"
            SlotSet("order_id", order_id)
            print(f"{message}\n{error_name} error")
        elif(error_code == '1'):
            message = "Your order is on hold due to invaid email.\n Please enter your new email to update."
            error_name = "email"
        elif(error_code == '2'):
            message = "Your order is on hold due to invaid zipcode.\n Please enter your new zipcode to update."
            error_name = "zipcode"
        elif(error_code == '3'):
            message = "Your order is on hold due to invaid zipcode and email.\n Please enter your new zipcode and email to update."
            error_name = "email and zipcode"
        elif(error_code == '5'):
            message = "Your Order Id is Invalid. Please enter your order id again."
            error_name = "order id"
            SlotSet("order_id", None)

        dispatcher.utter_message(text=message)

        return [SlotSet("error_code", error_code), SlotSet("error_name",error_name)]


# UPDATE ORDER STATUS

class ActionUpdateOrderDetails(Action):
    
    def name(self) -> Text:
        return "action_update_order_details"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        order_id = tracker.get_slot("order_id")
        error_code = tracker.get_slot("error_code")
        print(error_code)
        error_name = tracker.get_slot("error_name")

        email = tracker.get_slot("email")
        print(f"new_email = {email}")
        zipcode = tracker.get_slot("zipcode")
        print(f"new_zipcode = {zipcode}")
        
        if(error_code == '0'):
            if zipcode:
                if email:
                    data = {"zip":zipcode, "email":email}
                    error_name = "zipcode and email both"
                else:
                    data = {"zip":zipcode}
                    error_name = "zipcode"
            else:
                if email:
                    data = {"email":email}
                    error_name = "email"

        elif(error_code=='1'):
            data = {"email": email}
        
        elif(error_code=='2'):
            data = {"zip": zipcode}

        elif(error_code=='3'):
            data = {"zip":zipcode, "email":email}

        result = requests.post(f"https://dell-backend.herokuapp.com/order/{order_id}/{error_code}",json=data).json()
        print(result)
        code = result['code']

        if code == 0:
            dispatcher.utter_message(text=f"Your {error_name} has been updated and your order is processed now.")
        else:
            dispatcher.utter_message("Please enter a valid value")
            
        return[]


# PATTERN TYPE FORM ACTIVE


class ActionPatternType(Action):
    
    def name(self) -> Text:
        return "pattern_type_form"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        required_slots = ["pattern_type"]
        
        for slot_name in required_slots:
            if tracker.slots.get(slot_name) is None:
                return[SlotSet("requested_slot", slot_name)]
        
            
        return[SlotSet("requested_slot", None)]

# PATTERN TYPE FORM SUBMIT


class ActionSubmitPatternType(Action):
    
    def name(self) -> Text:
        return "action_submit_pattern_type"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        pattern_type = tracker.get_slot("pattern_type")
        print(pattern_type)

        words = nltk.word_tokenize(pattern_type)
        for word in words:
            if word == "day" or word == "1":
                pattern_type = "day"
                days = 0
            elif word == "week" or word == "2":
                pattern_type = "week"
                days = 7
            elif word == "month" or word == "3":
                pattern_type = "month"
                days = 30
        result = requests.get(f"https://genreport-nodejs.herokuapp.com/genReport/{days}")
            
        dispatcher.utter_message("https://genreport-nodejs.herokuapp.com/reports")
        return[SlotSet("pattern_type", None)]


# HISTORY TYPE FORM ACTIVE

class ActionhistoryType(Action):
    
    def name(self) -> Text:
        return "history_type_form"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        required_slots = ["history_type"]
        
        for slot_name in required_slots:
            if tracker.slots.get(slot_name) is None:
                return[SlotSet("requested_slot", slot_name)]
        
            
        return[SlotSet("requested_slot", None)]

# HISTORY TYPE FORM SUBMIT


class ActionSubmithistoryType(Action):
    
    def name(self) -> Text:
        return "action_submit_history_type"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        history_type = tracker.get_slot("history_type")
        print(history_type)

        words = nltk.word_tokenize(history_type)
        for word in words:
            if word == "day" or word == "1":
                history_type = "day"
            elif word == "week" or word == "2":
                history_type = "week"
            elif word == "month" or word == "3":
                history_type = "month"
            
        dispatcher.utter_message(text = f"https://dell-backend.herokuapp.com/excel/{history_type}")
       
        return[SlotSet("history_type", None)]

