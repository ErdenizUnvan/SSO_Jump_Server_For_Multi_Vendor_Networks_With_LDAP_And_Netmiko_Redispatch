from netmiko import ConnectHandler, redispatch
import time
import platform
import os
import re
from multiprocessing.dummy import Pool as ThreadPool

server_ip='192.168.218.204'

results=[]

devices=['192.168.218.181','192.168.218.182','192.168.218.183','192.168.218.184']

IDENTIFY_COMMANDS=['show version','display version']

user = 'student1'
sifre = 'Passw0rd1'      # sen ne kullanıyorsan

def ping_device(ip):
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    null = 'nul' if platform.system().lower() == 'windows' else '/dev/null'
    response = os.system(f"ping {param} 1 {ip} > {null} 2>&1")
    return response == 0

def device_type_detect(ip):
    if not ping_device(ip):
        results.append({'ip':ip, 'ping':False, 'sso_ssh':False, 'device_ssh':False, 'device_type':False})
        print(f'ip:{ip}, ping:False, sso_ssh:False, device_ssh:False, device_type:False\n')
        return

    print(f'ip:{ip}, ping:True')
    print('Connecting to SSO server')
    try:
        server = {
            'device_type': 'terminal_server',
            'host': server_ip,
            'username': user,
            'password': sifre,
            'port': 2222,
            'conn_timeout': 80,
            'global_delay_factor': 40,
            'session_log': 'outputx.log'
        }

        jump_conn = ConnectHandler(**server)
        print('servera baglandik')
    except Exception as e:
        results.append({'ip':ip,
                         'ping':True,
                         'sso_ssh':False,
                         'device_ssh':False,
                         'device_type':False})

        print(e)
        print(f'ip:{ip},sso_ssh:False, device_ssh:False, device_type:False\n')
        return
    #burada kaldik 13:00 oglen molasi sonrasi
    else:
        try:
            print('try')

            jump_conn.read_until_pattern(pattern='search or select one:',
                                         read_timeout=40)

            print(f'>> IP gönderiliyor: {ip}')
            jump_conn.write_channel(f"{ip}\n")

            jump_conn.read_until_pattern(pattern=r"[Pp]assword:",read_timeout=50)

            print('>> Cihaz şifresi gönderiliyor')
            jump_conn.write_channel(f"{server['password']}\n")

            prompt_out = jump_conn.read_until_pattern(pattern=r"[>#]",read_timeout=50)
            print('>> Prompt geldi:')
            print(prompt_out)

            redispatch(jump_conn, device_type='autodetect')

            device_type = None
            for cmd in IDENTIFY_COMMANDS:
                print(f'input: {cmd}\n')
                jump_conn.write_channel(f'{cmd}\n')
                time.sleep(1)
                output=jump_conn.read_channel()

                if 'Huawei' in output or 'HUAWEI' in output:
                    device_type = 'huawei'
                    break
                elif 'Cisco' in output:
                    if 'Cisco IOS-XE software,' in output or 'IOS-XE ROMMON' in output:
                        device_type = 'cisco_xe'
                        break
                    elif 'Cisco IOS Software' in output:
                        device_type = 'cisco_ios'
                        break
                    elif 'Cisco Nexus Operating System' in output:
                        device_type = 'cisco_nxos'
                        break
                    elif 'Cisco IOS XR Software' in output:
                        device_type = 'cisco_xr'
                        break

                elif 'Arista' in output:
                    device_type = 'arista_eos'
                    break

            if device_type:
                results.append({'ip':ip,
                 'ping':True,
                 'sso_ssh':True,
                 'device_ssh':True,
                 'device_type':device_type})

                print(f'ip:{ip},sso_ssh:True, device_ssh:True, device_type:{device_type}\n')

            if not device_type:
                results.append({'ip':ip,
                 'ping':True,
                 'sso_ssh':True,
                 'device_ssh':True,
                 'device_type':False})
                print(f'ip:{ip}, sso_ssh:True, device_ssh:True, device_type:False\n')

        except Exception as e:

            results.append({'ip':ip,
                 'ping':True,
                 'sso_ssh':True,
                 'device_ssh':False,
                 'device_type':False})
            print(f'ip:{ip},sso_ssh:True, device_ssh:False, device_type:False')
            print(e)
        finally:
            jump_conn.disconnect()


myPool = ThreadPool(4)
result = myPool.map(device_type_detect, devices)
