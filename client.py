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
        self.contacts = []

        self.add_event_handler('session_start', self.start)
        self.add_event_handler('message',self.receive)
        self.add_event_handler("presence_subscribe", self.subscribeNotification)


        self.register_plugin('xep_0077')
        self.register_plugin('xep_0030') # Service Discovery
        self.register_plugin('xep_0199') # XMPP Ping
        self.register_plugin('xep_0004') # Data forms
        self.register_plugin('xep_0077') # In-band Registration
        self.register_plugin('xep_0045') # Mulit-User Chat (MUC)
        self.register_plugin('xep_0096') # Send file 
        self.register_plugin('xep_0065')

        if self.connect():
            print('Ya estas conectado :D')
            self.process(block=False)
        else:
            raise Exception("No se pudo conectar!!! D:")

    def subscribeNotification(self, presence):
        user = presence['from']
        print(f"**{user} te agrego!**")
    
    def close(self):
        print('Cerrando la coneccion XMPP...')
        self.disconnect(wait=False)

    def start(self, event):
        self.send_presence(pshow='chat', pstatus='Conectado')
        roaster = self.get_roster()
        for user in roster['roster']['items'].keys():
            self.contacts.append(user)
        for jid in self.contacts:
            self.notificate(jid)
    
    def notificate(self, jid):
        message = self.Message()
        message['to'] = jid
        message['type'] = 'chat'
        message['body'] = 'Ya estoy conectado!!!'
        xml = ET.fromstring("<active xmlns='http://jabber.org/protocol/chatstates'/>")
        message.append(xml)
        try:
            message.send()
        except IqError as e:
            print(f"No se pudo notificar que estas conectado\n {e.iq['error']['text']}")
            self.disconnect()
        except IqTimeout:
            print("El server no responde D:")
            self.disconnect()



    def send_msg(self):
        message = self.Message()
        message['to'] = input('Usuario al que enviar mensaje: ')
        message['type'] = 'chat'
        message['body'] = input('Mensaje: ')
        print(f"Sendind message: {message['body'] }")
        message.send()
        print('Mensaje enviado!')

    def receive(self, message):
        print(f"{message['type']} {message['from'].user}> {message['body']}")

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
        iq['from'] = self.boundjid.bare
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
            self.send_presence_subscription(pto=username+'@redes2020.xyz')
            print('Se agregó el usuario', username)
        except IqError as e:
            print('No se pudo agregar usuario a los contactos',e)
        except IqTimeout:
            print("El server no responde D:")
            self.disconnect()

    def userInfo(self):
        username = input('Username que desea consultar: ')
        iq = self.Iq()
        iq['type'] = 'set'
        iq['id'] = 'search_result'
        iq['to'] = 'search.redes2020.xyz'
        iq['from'] = self.boundjid.bare

        item = ET.fromstring("<query xmlns='jabber:iq:search'>\
                                <x xmlns='jabber:x:data' type='submit'>\
                                    <field type='hidden' var='FORM_TYPE'>\
                                        <value>jabber:iq:search</value>\
                                    </field>\
                                    <field var='Username'>\
                                        <value>1</value>\
                                    </field>\
                                    <field var='search'>\
                                        <value>" + username + '@redes2020.xyz'+ "</value>\
                                    </field>\
                                </x>\
                              </query>")
        iq.append(item)
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
            print('No se pudo agregar usuario a los contactos',e)
        except IqTimeout:
            print("El server no responde D:")
            self.disconnect()

    def joinRoom(self):
        room = input('Nombre de la sala: ')
        nickname = input('Nickname: ')
        self.plugin['xep_0045'].joinMUC(room, nickname, wait=True)

    def sendMessageToRoom(self):
        room = input('Nombre de la sala: ')
        message = input('Mensaje: ')
        self.send_message(mto=room, mbody=message, mtype='groupchat')

    def changePresence(self):
        status = input("Nuevo mensaje de presencia: ")
        self.send_presence(pshow='chat', pstatus=status)



        

    
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
                    'Mostrar detalles de un usuario',
                    'Enviar mensaje directo',
                    'Ingresar a una conversación grupal',
                    'Enviar mensaje a un grupo',
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
            
            if menu == 'Mostrar detalles de un usuario':
                print(client.userInfo())

            if menu == 'Enviar mensaje directo':
                client.send_msg()

            if menu == 'Ingresar a una conversación grupal':
                client.joinRoom()

            if menu == 'Enviar mensaje a un grupo':
                client.sendMessageToRoom()










        


        