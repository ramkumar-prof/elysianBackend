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
    logger.info("🔧 Initializing PhonePe client")
    client_secret = CLIENT_SECRET
    client_id = CLIENT_ID
    client_version = CLIENT_VERSION
    env = Env.SANDBOX
    should_publish_events = False

    try:
        logger.debug(f"📡 Creating PhonePe client with ID: {client_id[:8]}..., Version: {client_version}, Env: {env}")
        client = StandardCheckoutClient.get_instance(
            client_id=client_id,
            client_secret=client_secret,
            client_version=client_version,
            env=env,
            should_publish_events=should_publish_events
        )
        logger.info("✅ PhonePe client created successfully")
        return client
    except Exception as e:
        logger.error(f"❌ Error creating PhonePe client: {e}")
        logger.error(f"🔍 Client creation error details: {type(e).__name__}: {e}")
        raise

def initiate_payment(amount, order_id, callback_url):
    """
    Initiate a payment request with PhonePe
    """
    logger.info(f"💳 Initiating payment for order {order_id}")
    logger.info(f"💰 Payment amount: ₹{amount/100:.2f} (₹{amount} paisa)")
    logger.info(f"🔗 Callback URL: {callback_url}")

    try:
        logger.debug("📋 Creating payment metadata")
        meta_info = MetaInfo(udf1="udf1", udf2="udf2", udf3="udf3")

        logger.debug("🔧 Getting PhonePe client")
        client = get_client()

        logger.debug(f"📝 Building payment request for order {order_id}")
        standard_pay_request = StandardCheckoutPayRequest.build_request(
            merchant_order_id=str(order_id),
            amount=int(amount),
            redirect_url=callback_url,
            meta_info=meta_info
        )

        logger.info(f"📡 Sending payment request to PhonePe for order {order_id}")
        standard_pay_response = client.pay(standard_pay_request)

        logger.info(f"✅ Payment initiated successfully for order {order_id}")
        logger.debug(f"📊 PhonePe response: {standard_pay_response}")
        print("===================", standard_pay_response)

        return standard_pay_response
    except Exception as e:
        logger.error(f"❌ Error initiating payment for order {order_id}: {e}")
        logger.error(f"🔍 Payment initiation error details: {type(e).__name__}: {e}")
        logger.error(f"💰 Failed payment details - Amount: ₹{amount/100:.2f}, Order: {order_id}")
        raise


def create_sdk_order_request(amount, order_id, callback_url):
    """
    Create an SDK order request for PhonePe
    """
    logger.info(f"📱 Creating SDK order request for order {order_id}")
    logger.info(f"💰 SDK order amount: ₹{amount/100:.2f}")

    try:
        logger.debug("📋 Creating SDK order metadata")
        meta_info = MetaInfo(udf1="udf1", udf2="udf2", udf3="udf3")

        logger.debug(f"📝 Building SDK order request for order {order_id}")
        sdk_order_request = CreateSdkOrderRequest.build_standard_checkout_request(
            merchant_order_id=order_id,
            amount=amount,
            meta_info=meta_info,
            redirect_url=callback_url
        )

        logger.debug("🔧 Getting PhonePe client for SDK order")
        client = get_client()

        logger.info(f"📡 Sending SDK order request to PhonePe for order {order_id}")
        sdk_order_response = client.create_sdk_order(sdk_order_request)

        logger.info(f"✅ SDK order created successfully for order {order_id}")
        return sdk_order_response
    except Exception as e:
        logger.error(f"❌ Error creating SDK order for order {order_id}: {e}")
        logger.error(f"🔍 SDK order error details: {type(e).__name__}: {e}")
        raise


def get_payment_status(order_id):
    """
    Get payment status from PhonePe for a given order ID
    """
    logger.info(f"🔍 Checking payment status for order: {order_id}")

    try:
        logger.debug("🔧 Getting PhonePe client for status check")
        client = get_client()

        logger.info(f"📡 Requesting payment status from PhonePe for order: {order_id}")
        # Use the correct method signature for get_order_status
        response = client.get_order_status(order_id)

        logger.info(f"✅ Payment status retrieved successfully for order: {order_id}")
        logger.debug(f"📊 Payment status response: {response}")
        print("Payment status response: ", response)

        return response
    except Exception as e:
        logger.error(f"❌ Error checking payment status for order {order_id}: {e}")
        logger.error(f"🔍 Payment status error details: {type(e).__name__}: {e}")
        # Return a default response structure for error cases
        return None


def initiate_refund(refund_id, order_id, amount):
    """
    Initiate a refund request with PhonePe
    """
    logger.info(f"💸 Initiating refund for order {order_id}")
    logger.info(f"🆔 Refund ID: {refund_id}")
    logger.info(f"💰 Refund amount: ₹{amount/100:.2f}")

    try:
        logger.debug(f"📝 Building refund request for order {order_id}")
        refund_request = RefundRequest.build_refund_request(
            merchant_refund_id=refund_id,
            original_merchant_order_id=order_id,
            amount=amount
        )

        logger.debug("🔧 Getting PhonePe client for refund")
        client = get_client()

        logger.info(f"📡 Sending refund request to PhonePe for order {order_id}")
        refund_response = client.refund(refund_request)

        logger.info(f"✅ Refund initiated successfully for order {order_id}, refund ID: {refund_id}")
        return refund_response
    except Exception as e:
        logger.error(f"❌ Error initiating refund for order {order_id}: {e}")
        logger.error(f"🔍 Refund initiation error details: {type(e).__name__}: {e}")
        logger.error(f"💸 Failed refund details - Amount: ₹{amount/100:.2f}, Order: {order_id}, Refund ID: {refund_id}")
        raise


def refund_status(refund_id):
    """
    Get refund status from PhonePe for a given refund ID
    """
    logger.info(f"🔍 Checking refund status for refund ID: {refund_id}")

    try:
        logger.debug("🔧 Getting PhonePe client for refund status check")
        client = get_client()

        logger.info(f"📡 Requesting refund status from PhonePe for refund ID: {refund_id}")
        response = client.get_refund_status(merchant_refund_id=refund_id)

        logger.info(f"✅ Refund status retrieved successfully for refund ID: {refund_id}")
        return response
    except Exception as e:
        logger.error(f"❌ Error checking refund status for refund ID {refund_id}: {e}")
        logger.error(f"🔍 Refund status error details: {type(e).__name__}: {e}")
        raise
