from django.urls import re_path
from .consumers import RelayConsumerConnections,OneTimeRequest,subTask,filePass

websocket_urlpatterns = [
    re_path(r"ws/relay/(?P<userId>\w+)/$", RelayConsumerConnections.as_asgi()),
    re_path(r"ws/relay/request/(?P<userId>\w+)/$", OneTimeRequest.as_asgi()),
    re_path(r"ws/relay/subTask/(?P<userId>\w+)/$", subTask.as_asgi()),
    re_path(r"ws/relay/sendFile/(?P<transactionId>\w+)/(?P<userId>\w+)/$", filePass.as_asgi())
]