import requests
import json


class vy:
    def __init__(self):
        url = 'https://192.168.3.34/retrieve'
        playoad = {'data': '{"op": "showConfig", "path": []}', 'key': '100'}
        headers = {}
        response = requests.request("POST", url, headers=headers, data=playoad, verify=False)
        json_object = json.dumps(response.text, indent=8)
        print(json_object)


    def set(ethnb, ip):
            url = 'https://192.168.3.34/configure'
            playoad = {'data': '{"op": "set", "path": ["interfaces", "ethernet", "'+str(ethnb)+'", "address", "'+str(ip)+'"]}',
                       'key': '100'}
            headers = {}
            response = requests.request("POST", url, headers=headers, data=playoad, verify=False)
            print(response.text)
            return response.text


vy()
vy.set("eth1", "192.168.3.200/24")