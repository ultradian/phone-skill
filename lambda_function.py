"""lambda_function.py: example phone Alexa skill."""
import logging

from ask_sdk.standard import StandardSkillBuilder
from ask_sdk_core.dispatch_components import (
    AbstractRequestHandler, AbstractExceptionHandler)
from ask_sdk_core.utils import is_intent_name, is_request_type

sb = StandardSkillBuilder(table_name="PhoneTable", auto_create_table=True)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for skill launch."""

    def can_handle(self, handler_input):
        """Can handle or not."""
        return is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        """Handle response."""
        logger.info("In LaunchRequestHandler")
        # get attributes from DynamoDB table
        session_attr = handler_input.attributes_manager.persistent_attributes
        if not session_attr:
            # first time
            speech = "Hi. What is your phone number?"
            reprompt = "What is your phone number?"
        else:
            if 'phone' in session_attr and session_attr['phone']:
                phone = session_attr['phone']
                reprompt = ("Tell me a different phone number, or say "
                            "stop to quit. ")
                speech = ("I have your phone number as  <say-as "
                          f"interpret-as='telephone'>{phone}</say-as>")
                speech += reprompt
            else:
                reprompt = "What is your phone number?"
                speech = "Welcome back. " + reprompt
        # put attributes into session storage
        handler_input.attributes_manager.session_attributes = session_attr
        handler_input.response_builder.speak(speech).ask(reprompt)
        return handler_input.response_builder.response


class PhoneNumberIntentHandler(AbstractRequestHandler):
    """Handler for PhoneNumberIntent."""

    def can_handle(self, handler_input):
        """Can handle or not."""
        return is_intent_name("PhoneNumberIntent")(handler_input)

    def handle(self, handler_input):
        """Handle response."""
        logger.info("In PhoneNumberIntentHandler")
        session_attr = handler_input.attributes_manager.session_attributes
        phone = (handler_input.request_envelope.request.intent
                 .slots['phone'].value)
        if 'phone' not in session_attr or session_attr['phone'] != phone:
                # replace phone number
                session_attr['phone'] = phone
        reprompt = "Tell me a different phone number, or say stop to quit. "
        speech = ("Saving your phone number as <say-as "
                  f"interpret-as='telephone'>{phone}</say-as>. " + reprompt)
        handler_input.attributes_manager.session_attributes = session_attr
        handler_input.response_builder.speak(speech).ask(reprompt)
        return handler_input.response_builder.response


class ExitIntentHandler(AbstractRequestHandler):
    """Handler for Cancel, Stop intents."""

    def can_handle(self, handler_input):
        """Can handle or not."""
        return (is_intent_name("AMAZON.CancelIntent")(handler_input) or
                is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        """Handle response."""
        logger.info("In ExitIntentHandler")
        speech = "Goodbye. "
        session_attr = handler_input.attributes_manager.session_attributes
        handler_input.attributes_manager.persistent_attributes = session_attr
        handler_input.attributes_manager.save_persistent_attributes()
        handler_input.response_builder.speak(speech)
        handler_input.response_builder.set_should_end_session(True)
        return handler_input.response_builder.response


class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for skill session end."""

    def can_handle(self, handler_input):
        """Can handle or not."""
        return is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        """Handle response."""
        logger.info("In SessionEndedRequestHandler")
        reason = handler_input.request_envelope.request.reason
        logger.info(f"Session ended with reason: {reason}")
        session_attr = handler_input.attributes_manager.session_attributes
        # save session attributes to DynamoDB
        handler_input.attributes_manager.persistent_attributes = session_attr
        handler_input.attributes_manager.save_persistent_attributes()
        logger.info(f"saving attributes: {session_attr}")
        return handler_input.response_builder.response


# Exception Handler classes
class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Catch All Exception handler.

    This handler catches all kinds of exceptions and prints
    the stack trace on AWS Cloudwatch with the request envelope.
    """

    def can_handle(self, handler_input, exception):
        """Can handle or not."""
        return True

    def handle(self, handler_input, exception):
        """Handle response."""
        logger.error(exception, exc_info=True)
        request = handler_input.request_envelope.request
        logger.info(f"Original request was {request}")
        speech = "Sorry, there was a problem. Please try again!!"
        handler_input.response_builder.speak(speech).ask(speech)
        return handler_input.response_builder.response


# Add all request handlers to the skill.
sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(PhoneNumberIntentHandler())
sb.add_request_handler(ExitIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())

# Add exception handler to the skill.
sb.add_exception_handler(CatchAllExceptionHandler())

# Expose the lambda handler to register in AWS Lambda.
lambda_handler = sb.lambda_handler()
