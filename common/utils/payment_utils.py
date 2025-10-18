from phonepe.sdk.pg.payments.v2.standard_checkout_client import StandardCheckoutClient
from phonepe.sdk.pg.env import Env
from elysianBackend.constants import CLIENT_ID, CLIENT_SECRET, CLIENT_VERSION, PAYMENT_ENV
from phonepe.sdk.pg.common.models.request.meta_info import MetaInfo
from phonepe.sdk.pg.payments.v2.models.request.standard_checkout_pay_request import StandardCheckoutPayRequest
from phonepe.sdk.pg.payments.v2.models.request.create_sdk_order_request import CreateSdkOrderRequest
from phonepe.sdk.pg.common.models.request.refund_request import RefundRequest
from phonepe.sdk.pg.subscription.v2.subscription_client import SubscriptionClient

import json
import logging

logger = logging.getLogger(__name__)

def get_client():
    """
    Create and return a PhonePe StandardCheckoutClient instance
    """
    client_secret = CLIENT_SECRET
    client_id = CLIENT_ID
    client_version = CLIENT_VERSION
    env = Env.SANDBOX
    should_publish_events = False

    try:
        client = StandardCheckoutClient.get_instance(
            client_id=client_id,
            client_secret=client_secret,
            client_version=client_version,
            env=env,
            should_publish_events=should_publish_events
        )
        return client
    except Exception as e:
        logger.error(f"Error creating PhonePe client: {e}")
        raise

def initiate_payment(amount, order_id, callback_url):
    """
    Initiate a payment request with PhonePe
    """
    try:
        meta_info = MetaInfo(udf1="udf1", udf2="udf2", udf3="udf3")
        client = get_client()
        standard_pay_request = StandardCheckoutPayRequest.build_request(
            merchant_order_id=str(order_id),
            amount=int(amount),
            redirect_url=callback_url,
            meta_info=meta_info
        )
        standard_pay_response = client.pay(standard_pay_request)
        print("===================", standard_pay_response)
        logger.info(f"Payment initiated for order {order_id} and response: {standard_pay_response}")
        return standard_pay_response
    except ExceptiOrderStatusResponseon as e:
        logger.error(f"Error initiating payment for order {order_id}: {e}")
        raise


def create_sdk_order_request(amount, order_id, callback_url):
    """
    Create an SDK order request for PhonePe
    """
    try:
        meta_info = MetaInfo(udf1="udf1", udf2="udf2", udf3="udf3")
        sdk_order_request = CreateSdkOrderRequest.build_standard_checkout_request(
            merchant_order_id=order_id,
            amount=amount,
            meta_info=meta_info,
            redirect_url=callback_url
        )
        client = get_client()
        sdk_order_response = client.create_sdk_order(sdk_order_request)
        return sdk_order_response
    except Exception as e:
        logger.error(f"Error creating SDK order for order {order_id}: {e}")
        raise


def get_payment_status(order_id):
    """
    Get payment status from PhonePe for a given order ID
    """
    try:
        client = get_client()
        logger.info(f"Checking payment status for order: {order_id}")

        # Use the correct method signature for get_order_status
        response = client.get_order_status(order_id)
        print("Payment status response: ", response)

        return response
    except Exception as e:
        logger.error(f"Error checking payment status for order {order_id}: {e}")
        # Return a default response structure for error cases
        return None


def initiate_refund(refund_id, order_id, amount):
    """
    Initiate a refund request with PhonePe
    """
    try:
        refund_request = RefundRequest.build_refund_request(
            merchant_refund_id=refund_id,
            original_merchant_order_id=order_id,
            amount=amount
        )
        client = get_client()
        refund_response = client.refund(refund_request)
        logger.info(f"Refund initiated for order {order_id}, refund ID: {refund_id}")
        return refund_response
    except Exception as e:
        logger.error(f"Error initiating refund for order {order_id}: {e}")
        raise


def refund_status(refund_id):
    """
    Get refund status from PhonePe for a given refund ID
    """
    try:
        client = get_client()
        response = client.get_refund_status(merchant_refund_id=refund_id)
        logger.info(f"Refund status checked for refund ID: {refund_id}")
        return response
    except Exception as e:
        logger.error(f"Error checking refund status for refund ID {refund_id}: {e}")
        raise
