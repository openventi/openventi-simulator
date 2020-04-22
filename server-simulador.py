#!/usr/bin/env python

import sys
import asyncio
import websockets
import json
import time
import math
import random
import logging

logging.basicConfig(
    filename="app.log",
    level=logging.WARNING,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger(__name__)

SENSOR_FREQ = int(sys.argv[2])
ALERT_FREQ = int(sys.argv[3])

CLIENTS = set()

parameters = {
    "rr": 0,
    "o2": 0,
    "peep": 0,
    "tv": 0,
}

patient = {
    "name": "",
    "medical_history_number": "",
    "bed_number": "",
    "atention_number": "",
}

alerts = {
    "volume": [0, 0],
    "flow": [0, 0],
    "presure": [0, 0],
}

config_versions = [time.time()]

random_data = {
    "parameters": {
        "rr": 0,
        "o2": 0,
        "peep": 0,
        "tv": 0,
    },
    "alert_id": 0,
}


async def manageConn(websocket, path):
    CLIENTS.add(websocket)
    await asyncio.wait([
        respondEvents(websocket, path),
        streamData(websocket, path),
        pushConfig(websocket, path),
    ])
    CLIENTS.remove(websocket)


async def alertGenerator():
    global random_data
    while True:
        random_data["alert_id"] += 1
        for cli in CLIENTS:
            await pushAlert(cli)
        await asyncio.sleep(ALERT_FREQ)


async def sensorGenerator():
    global parameters
    global random_data
    while True:
        for parameter in random_data["parameters"]:
            random_data["parameters"][parameter] = (
                float(parameters[parameter]) + random.random())
        for cli in CLIENTS:
            await pushSensor(cli)
        await asyncio.sleep(SENSOR_FREQ)


async def pushSensor(websocket):
    global random_data
    try:
        data = {
            "t": 3,
            "type": "sensors_push",
            "data": random_data["parameters"],
            "ts": str(time.time()),
            "token": "10293848129381038109238019380913",
        }
        data = json.dumps(data)
        await websocket.send(data)
        # print("> " + data)
    except:
        return


async def pushConfig(websocket, path):
    global config_versions
    checker = 0
    while True:
        try:
            if checker < config_versions[0]:  # todo: ver
                models = ["parameters", "patient", "alerts"]
                for model in models:
                    data = {
                        "t": 2,
                        "type": "push",
                        "model": model,
                        "data": globals()[model],
                        "ts": str(time.time()),
                        "token": "10293848129381038109238019380913",
                    }

                    await websocket.send(json.dumps(data))
                # print("> " + data)
                checker = config_versions[0]
            await asyncio.sleep(1)
        except:
            break


async def pushAlert(websocket):
    global random_data
    try:
        data = {
            "t": 1,
            "type": "alert",
            "message": "Alerta de prueba " + str(random_data["alert_id"]),
            "severity": 1,
        }
        await websocket.send(json.dumps(data))
        # print("> " + data)
    except:
        return


async def streamData(websocket, path):
    while True:
        try:
            factor = 20
            current_time = time.time()
            data = {
                "t": 0,
                "type": "stream",
                "data": {
                    "volume": str(factor + factor * math.sin(current_time)),
                    "presure": str(factor + factor * math.cos(current_time)),
                    "flow": str(factor + factor * math.sin(2 * current_time)),
                },
            }

            result = json.dumps(data)
            await websocket.send(result)
            await asyncio.sleep(0.1)
            # print(f"> {result}")
        except:
            break


async def respondEvents(websocket, path):
    # global parameters
    global config_versions
    while True:
        try:
            request = await websocket.recv()
            request = json.loads(request)
            print(f"< {request}")
            response = ""
            model = request["model"]

            if request["action"] == "set":
                response = {
                    "id": str(request["id"]),
                    "status": 200,
                    "token": "asdf",
                }
                globals()[model] = request["data"]
                config_versions[0] = time.time()
                print("new_config= " + str(config_versions[0]))
            elif request["action"] == "get":
                response = {
                    "id": str(request["id"]),
                    "status": 300,
                    "model": model,
                    "data": globals()[model],
                    "token": "aaaaaasdf",
                }
            else:
                response = {
                    "id": str(request["id"]),
                    "status": -1,
                    "token": "asdf",
                }

            response = json.dumps(response)
            await websocket.send(response)
            print(f"> {response}")
        except ZeroDivisionError as err:
            logger.error(err)
            print("Connection closed")
            break


start_server = websockets.serve(manageConn, "0.0.0.0", int(sys.argv[1]))

asyncio.get_event_loop().run_until_complete(start_server)
l = asyncio.get_event_loop()
l.create_task(alertGenerator())
l.create_task(sensorGenerator())
l.run_forever()
