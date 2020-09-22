import questionary
import sleekxmpp
import ssl

class Client(sleekxmpp.ClientXMPP):
    def __init__(self, username, password, instance_name='redes2020.xyz'):
        sleekxmpp.ClientXMPP.__init__(self, username, password)
        self.username = username

        self.add_event_handler('session_start', self.start, threaded=False, disposable=True)
        self.add_event_handler('message',self.receive, threaded=True, disposable=False)

        if self.connect():
            print('Ya estas conectado :D')
            self.process(block=False)
        else:
            raise Exception("No se pudo conectar!!! D:")
    
    def close(self):
        print('Cerrando la coneccion XMPP...')
        self.disconnect(wait=False)

    def start(self, event):
        self.send_presence()
        self.get_roster()

    def send_msg(self, to, body):
        message = self.Message()
        message['to'] = to
        message['type'] = 'chat'
        message['body'] = body
        print(f"Sendind message: {body}")
        message.send()

    def receive(self, message):
        if message['type'] in ('chat', 'normal'):
            print(f"{message['from'].user}> {message['body']}")

    


        


        