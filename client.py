import questionary
import sleekxmpp
import ssl
from sleekxmpp.exceptions import IqError, IqTimeout

class Register(sleekxmpp.ClientXMPP):
    def __init__(self, jid, password):
        self.add_event_handler('session_start', self.start, threaded=True)
        self.add_event_handler('register', self.register, threaded=True)
        xmpp = RegisterBot(opts.jid, opts.password)
        xmpp.register_plugin('xep_0030') # Service Discovery
        xmpp.register_plugin('xep_0004') # Data forms
        xmpp.register_plugin('xep_0066') # Out-of-band Data
        xmpp.register_plugin('xep_0077') # In-band Registration

    def start(self, event):
        self.send_presence()
        self.get_roster()
        self.disconnect()

    def register(self, iq):
        resp = self.Iq()
        resp['type'] = 'set'
        resp['register']['username'] = self.boundjid.user
        resp['register']['password'] = self.password

        try:
            resp.send(now=True)
            print(f"Se creo el usuario para {self.boundjid}")
        except IqError as e:
            print(f"No se pudo crear el usuario: {e.iq['error']['text']}")
            self.disconnect()
        except IqTimeout:
            print("El server no responde D:")
            self.disconnect()
        

class Client(sleekxmpp.ClientXMPP):
    def __init__(self, jid, password, instance_name='redes2020.xyz'):
        sleekxmpp.ClientXMPP.__init__(self, jid, password)
        self.username = jid

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

    def login(self):
        logged = False
        if self.connect():
            self.process()
            logged = True
            print('Has iniciado sesion!')
        else:
            print('No se pudo iniciar sesion.')
        return logged

    
if __name__ == '__main__':
    home = ''
    logged = False

    while home != 'Salir':
        if not logged:
            print('============= Inicio de Sesion =============')
            home = questionary.select(
                'Escoja una opcion',
                choices=['Salir', 'Iniciar Sesion', 'Registrarse']
            ).ask()

            if home == 'Iniciar Sesion':
                username = input('Username: ')
                password = input('Password: ')
                client = Cliente(username+'@redes2020.xyz', password)
                logged = client.login()

            elif home == 'Registrarse':
                username = input('Username: ')
                password = input('Password: ')
                registration = Register(username+'@redes2020.xyz',password)
                if registration.connect():
                    registration.process(block=True)
                    print('Usuario registrado!')
                else:
                    print('No se pudo registrar :(')

        else:
            chat = questionary.select(
                '=======================================',
                choices=[
                    'Cerrar sesion',
                    'Eliminar usuario',
                    'Mostrar todos los usuarios',
                    'Agregar un usuario a los contactos',
                    'Mostrar detalles de usuario',
                    'Enviar mensaje directo',
                    'Conversaciones grupales',
                    'Definir mensaje de presencia',
                    'Enviar archivo'
                ]
            )









        


        