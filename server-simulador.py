#!/usr/bin/env python

# WS server example

import asyncio
import websockets
import json
import time
import math
import random

SENSOR_FREQ = 3
ALERT_FREQ = 5

CLIENTS = set()

p = {
  "rr":0,
  "o2":0,
  "peep":0,
  "tv":0,
}
config_ver = [time.time()];

rand_sim = {
  "p":{
    "rr":0,
    "o2":0,
    "peep":0,
    "tv":0,
  },
  "alertid": 0,
}

async def manageConn(websocket, path):
  CLIENTS.add(websocket)
  await asyncio.wait([
    respondEvents(websocket,path),
    streamData(websocket,path),
    pushConfig(websocket,path),
  ])
  CLIENTS.remove(websocket)

async def alertGenerator():
  while(True):
    rand_sim['alertid'] += 1
    for cli in CLIENTS:
      await pushAlert(cli)
    await asyncio.sleep(ALERT_FREQ)

async def sensorGenerator():
  while(True):
    for k in rand_sim['p']:
      rand_sim['p'][k] = float(p[k]) + random.random()
    for cli in CLIENTS:
      await pushSensor(cli)
    await asyncio.sleep(SENSOR_FREQ)

async def pushSensor(websocket):
  try:
    sdata = '{"t":3,"sensores":'+json.dumps(rand_sim['p'])+',"ts":'+str(time.time())+',"token":"10293848129381038109238019380913"}'
    await websocket.send(sdata)
    print("> " + sdata)
  except:
    return

async def pushConfig(websocket, path):
  ccv = 0
  while(True):
    try:
      if (ccv < config_ver[0]):
        cfg = '{"t":2,"params":'+json.dumps(p)+',"ts":'+str(time.time())+',"token":"10293848129381038109238019380913"}'
        await websocket.send(cfg)
        print("> " + cfg)
        ccv = config_ver[0]
      await asyncio.sleep(1)
    except:
      break

async def pushAlert(websocket):
  try:
    err = '{"t":1,"msg":"Alerta de prueba '+str(rand_sim['alertid'])+'","severidad":1}'
    await websocket.send(err)
    print("> " + err)
  except:
    return

async def streamData(websocket, path):
  while(True):
    try:
      await websocket.send('{"t":0,"d":['+str(20+20*math.sin(time.time()))+','+str(20+20*math.cos(time.time()))+','+str(20+20*math.sin(2*time.time()))+']}')
      await asyncio.sleep(0.1)
    except:
      break

async def respondEvents(websocket, path):
  while(True):
    try:
      name = await websocket.recv()
      print(f"< {name}")
      j = json.loads(name)
      res =''

      if (j['action'] == 'set'):
        res = '{"id":'+str(j['id'])+',"status":200,"token":"asdf"}'
        p[j['param']] = j['value']
        config_ver[0] = time.time()
        print("new_config= "+str(config_ver[0]))
      elif (j['action'] == 'get'):
        res = '{"id":'+str(j['id'])+',"status":300,"value":'+str(p[j['param']])+',"token":"aaaaaasdf"}'
      else:
        res = '{"id":'+str(j['id'])+',"status":-1,"token":"asdf"}'

      await websocket.send(res)
      print(f"> {res}")
    except:
      print('Connection closed')
      break


start_server = websockets.serve(manageConn, "localhost", 8765)

asyncio.get_event_loop().run_until_complete(start_server)
l = asyncio.get_event_loop()
l.create_task(alertGenerator())
l.create_task(sensorGenerator())
l.run_forever()

