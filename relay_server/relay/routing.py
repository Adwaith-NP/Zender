from django.urls import re_path
from .consumers import RelayConsumerConnections,OneTimeRequest,ShearePublicKey

websocket_urlpatterns = [
    re_path(r"ws/relay/(?P<userId>\w+)/$", RelayConsumerConnections.as_asgi()),
    re_path(r"ws/relay/request/(?P<userId>\w+)/$", OneTimeRequest.as_asgi()),
    re_path(r"ws/relay/publicKey/(?P<userId>\w+)/$", ShearePublicKey.as_asgi()),
]