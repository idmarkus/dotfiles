import logging

logging.basicConfig(level=logging.DEBUG)
import asyncio
import simpleobsws

# class OBS:
#     OBS_URI = 'ws://localhost:4444'
#     password = ''
#     parameters = None

#     def __init__(self, _password):
#         self.password = _password
#         self.parameters = simpleobsws.IdentificationParameters()
#         self.parameters.eventSubscriptions = (1<<0) | (1<<2) # Subscribe to General and Scenes categories
#         self.ws = simpleobsws.WebSocketClient(url = self.OBS_URI,
#                                               password = self.password,
#                                               Identification_parameters = self.parameters)


#     async def on_event(self, eventType, eventData):

URI = "ws://localhost:4444"
PASSWORD = ""

parameters = simpleobsws.IdentificationParameters(ignoreNonFatalRequestChecks=False)
ws = simpleobsws.WebSocketClient(url=URI, password=PASSWORD, identification_parameters=parameters)


async def make_request():
    await ws.connect()
    await ws.wait_until_identified(timeout=5)

    request = simpleobsws.Request('GetVersion')

    ret = await ws.call(request)
    if ret.ok():
        print("Request ok! Response data: {}".format(ret.responseData), flush=True)

    await ws.disconnect()


loop = asyncio.get_event_loop()
loop.run_until_complete(make_request())
