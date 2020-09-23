import questionary
import sleekxmpp
import ssl
from sleekxmpp.exceptions import IqError, IqTimeout
from sleekxmpp.xmlstream.stanzabase import ET, ElementBase

# usuario oliver
# password oliver

class Register(sleekxmpp.ClientXMPP):
    def __init__(self, jid, password):
        sleekxmpp.ClientXMPP.__init__(self, jid, password)
        self.add_event_handler('session_start', self.start, threaded=True)
        self.add_event_handler('register', self.register, threaded=True)
        self.register_plugin('xep_0030') # Service Discovery
        self.register_plugin('xep_0004') # Data forms
        self.register_plugin('xep_0066') # Out-of-band Data
        self.register_plugin('xep_0077') # In-band Registration

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
            print(f"No se pudo crear el usuario\n {e.iq['error']['text']}")
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
        if self.connect():
            self.process()
            print('Has iniciado sesion!')
            return True
        else:
            print('No se pudo iniciar sesion.')
            return False

    def deleteUser(self):
        iq = self.make_iq_set(ito='redes2020.xyz', ifrom=self.boundjid.user)
        xml = ET.fromstring("<query xmlns='jabber:iq:register'>\
                                <remove/>\
                            </query>")
        iq.append(xml)
        
        try:
            response = iq.send()
            if response['type'] == 'result':
                print("Usuario eliminado")
        except IqError as e:
            print(f"No se pudo eliminar el usuario\n {e.iq['error']['text']}")
            self.disconnect()
        except IqTimeout:
            print("El server no responde D:")
            self.disconnect()

    def getUsers(self):
        iq = self.Iq()
        iq['type'] = 'set'
        iq['id'] = 'search_result'
        iq['to'] = 'search.redes2020.xyz'
        xml = ET.fromstring("<query xmlns='jabber:iq:search'>\
                                <x xmlns='jabber:x:data' type='submit'>\
                                    <field type='hidden' var='FORM_TYPE'>\
                                        <value>jabber:iq:search</value>\
                                    </field>\
                                    <field var='Username'>\
                                        <value>1</value>\
                                    </field>\
                                    <field var='search'>\
                                        <value>*</value>\
                                    </field>\
                                </x>\
                              </query>")
        iq.append(xml)
        try:
            response = iq.send()
            data = []
            temp = []
            cont = 0
            for i in response.findall('.//{jabber:x:data}value'):
                cont += 1
                txt = ''
                if i.text != None:
                    txt = i.text

                temp.append(txt)
                if cont == 4:
                    cont = 0
                    data.append(temp)
                    temp = []

            return data
        except IqError as e:
            print(f"No se pudo obtener el listado de usuarios\n {e.iq['error']['text']}")
            self.disconnect()
        except IqTimeout:
            print("El server no responde D:")
            self.disconnect()

    def addUser(self):
        username = input('Username que quiere agregar: ')
        try:
            self.send_presence_subscription(pto=username+'redes2020.xyz')
            print('Se agregó el usuario', username)
        except IqError as e:
            print('No se pudo agregar usuario a los contactos',e)
        except IqTimeout:
            print("El server no responde D:")
            self.disconnect()

        

    
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
                client = Client(username+'@redes2020.xyz', password)
                if client.login():
                    logged = True

            elif home == 'Registrarse':
                username = input('Username: ')
                password = input('Password: ')
                registration = Register(username+'@redes2020.xyz',password)
                if registration.connect():
                    registration.process(block=True)
                else:
                    print('No se pudo registrar :(')
        else:
            menu = questionary.select(
                '============== Menu ==============',
                choices=[
                    'Cerrar sesion',
                    'Eliminar usuario',
                    'Mostrar todos los usuarios',
                    'Agregar un usuario a los contactos',
                    'Mostrar detalles de un contacto',
                    'Enviar mensaje directo',
                    'Conversaciones grupales',
                    'Definir mensaje de presencia',
                    'Enviar archivo'
                ]
            ).ask()

            if menu == 'Eliminar usuario':
                client.deleteUser()
                menu = 'Cerrar sesion'

            if menu == 'Cerrar sesion':
                client.disconnect()
                logged = False

            if menu == 'Mostrar todos los usuarios':
                print(client.getUsers())

            if menu == 'Agregar un usuario a los contactos':
                client.addUser()










        


        