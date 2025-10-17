from phonepe.sdk.pg.payments.v2.standard_checkout_client import StandardCheckoutClient
from elysianBackend.constants import CLIENT_ID, CLIENT_SECRET, CLIENT_VERSION, PAYMENT_ENV
from phonepe.sdk.pg.common.models.request.meta_info import MetaInfo
from phonepe.sdk.pg.payments.v2.models.request.standard_checkout_pay_request import StandardCheckoutPayRequest
from phonepe.sdk.pg.payments.v2.models.request.create_sdk_order_request import CreateSdkOrderRequest
from phonepe.sdk.pg.common.models.request.refund_request import RefundRequest

 

def get_client():
    client_secret = CLIENT_SECRET
    client_id = CLIENT_ID
    client_version = CLIENT_VERSION  # insert your client version
    env = PAYMENT_ENV
    should_publish_events = False
    client = StandardCheckoutClient.get_instance(
        client_id=client_id,
        client_secret=client_secret,
        client_version=client_version,
        env=env,
        should_publish_events=should_publish_events
    )
    return client


def initiate_payment(amount, order_id, callback_url):
    meta_info = MetaInfo(udf1="udf1", udf2="udf2", udf3="udf3")
    standard_pay_request = StandardCheckoutPayRequest.build_request(
        merchant_order_id=order_id,
        amount=amount,
        redirect_url=callback_url,
        meta_info=meta_info
    )
    client = get_client()
    standard_pay_response = client.pay(standard_pay_request)
    return standard_pay_response


def create_sdk_order_request(amount, order_id, callback_url):
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


def get_payment_status(order_id):
    client = get_client()
    response = client.get_order_status(m_order_id=order_id, details=False)
    return response


def initiate_refund(refund_id, order_id, amount):
    refund_request = RefundRequest.build_refund_request(
        merchant_refund_id=refund_id,
        original_merchant_order_id=order_id,
        amount=amount
    )
    client = get_client()
    refund_response = client.refund(refund_request)
    return refund_response


def refund_status(refund_id):
    client = get_client()
    response = client.get_refund_status(merchant_refund_id=refund_id)
    return response
