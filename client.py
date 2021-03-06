import questionary
import sleekxmpp
import ssl
from sleekxmpp.exceptions import IqError, IqTimeout
from sleekxmpp.xmlstream.stanzabase import ET, ElementBase

import filetype
import base64
import time

# usuario oliver
# password oliver

## This class holds the logic for te user registration
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

    #Function that registers a user.
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
        
#This class holds all the logic and funtionality of the xmpp client
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
    
    # Notification that pops when someone subscribes to my user
    def subscribeNotification(self, presence):
        user = presence['from']
        print(f"**{user} te agrego!**")
    
    # Function that logs out from server
    def close(self):
        print('Cerrando la coneccion XMPP...')
        self.disconnect(wait=False)

    # Fuction that notifies every user that im connected and ready to chat
    def start(self, event):
        self.send_presence(pshow='chat', pstatus='Conectado')
        roaster = self.get_roster()
        for user in roster['roster']['items'].keys():
            self.contacts.append(user)
        for jid in self.contacts:
            self.notificate(jid)
    
    # function with the logic of sending the notification to every user that im connected
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

    # function that sends messages to an user
    def send_msg(self):
        message = self.Message()
        to = input('Usuario al que enviar mensaje: ')
        message['to'] = to+'@redes2020.xyz'
        message['type'] = 'chat'
        body = input('Mensaje: ')
        message['body'] = body
        print(f"Sendind message: {message['body'] }")
        message.send()
        # self.send_message(mto=to+'@redes2020.xyz', mbody=body, mtype='chat')
        print('Mensaje enviado!')

    # Function that reads incoming messages
    def receive(self, message):
        print()
        print(f"{message['from'].user}> {message['body']}")
        # print('recieved message')
        # if message['type'] in ('chat', 'normal'):
        #     if message['subject'] == 'file':
        #         body = message['body']
        #         image = body.encode('utf-8')
        #         image = base64.decodebytes(image)
        #         with open('archivo_'+str(int(time.time()))+ ".png", 'wb') as archivo:
        #             archivo.write(image)
        #         print(f"{message['from'].user}> Te envió un archivo! lo guardamos en el directorio del cliente.")
        #     else:
        #         print(f"{message['from'].user}> {message['body']}")

        # elif message['type'] == 'groupchat':
        #     print(f"Groupchat: {message['from'].user}> {message['body']}")
        
        # else:
        #     print(f"{message['from'].user}> {message['body']}")
        print()



    # Function with the login logic
    def login(self):
        if self.connect():
            self.process()
            print('Has iniciado sesion!')
            return True
        else:
            print('No se pudo iniciar sesion.')
            return False

    # Function that deletes my user from server
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

    # Function that shows every user on the server and its information
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

    # Function that adds an user to the contacts library
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

    # Function that request an especific user information
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

    # Function that joins you to a chat room
    def joinRoom(self):
        room = input('Nombre de la sala: ')
        nickname = input('Nickname: ')
        self.plugin['xep_0045'].joinMUC(room+"@conference.redes2020.xyz", nickname, wait=True, pstatus='Hooolaaa! ya me conecte!', pfrom=self.boundjid.full)
        self.plugin['xep_0045'].setAffiliation(room+"@conference.redes2020.xyz", self.boundjid.full, affiliation='owner')
        # self.plugin['xep_0045'].configureRoom(room+"@conference.redes2020.xyz", ifrom=self.boundjid.full)

    # Fucntion that sends message to a chat room
    def sendMessageToRoom(self):
        room = input('Nombre de la sala: ')
        message = input('Mensaje: ')
        room = room + '@conference.redes2020.xyz'
        self.send_message(mto=room, mbody=message, mtype='groupchat')

    # function that changes your user status on the server.
    def changePresence(self):
        status = input("Nuevo mensaje de presencia: ")
        self.send_presence(pshow='chat', pstatus=status)

    def sendFile(self):
        with open('./imagen.png') as img:
            image = base64.b64encode(img.read()).decode('utf-8')
        self.send_message(mto=to, mbody=image, msubject='file', mtype='chat')



        

    
if __name__ == '__main__':
    home = 10
    logged = False

    while home != 0:
        if not logged:
            print('\n\n============= Inicio de Sesion =============')
            print('0. Salir')
            print('1. Iniciar sesion')
            print('2. Register')
            home = int(input('Ingrese el numero de la opcion que desea: '))


            if home == 1:
                username = input('Username: ')
                password = input('Password: ')
                client = Client(username+'@redes2020.xyz', password)
                if client.login():
                    logged = True

            elif home == 2:
                username = input('Username: ')
                password = input('Password: ')
                registration = Register(username+'@redes2020.xyz',password)
                if registration.connect():
                    registration.process(block=True)
                else:
                    print('No se pudo registrar :(')
            
            else:
                print('Seleccione una opcion valida. \n')
        else:
            # menu = questionary.select(
            #     '============== Menu ==============',
            #     choices=[
            #         'Cerrar sesion',
            #         'Eliminar usuario',
            #         'Mostrar todos los usuarios',
            #         'Agregar un usuario a los contactos',
            #         'Mostrar detalles de un usuario',
            #         'Enviar mensaje directo',
            #         'Ingresar a una conversación grupal',
            #         'Enviar mensaje a un grupo',
            #         'Definir mensaje de presencia',
            #         'Enviar archivo'
            #     ]
            # ).ask()
            print('\n\n============== Menu ==============')
            print('1. Cerrar sesion'),
            print('2. Eliminar usuario'),
            print('3. Mostrar todos los usuarios'),
            print('4. Agregar un usuario a los contactos'),
            print('5. Mostrar detalles de un usuario'),
            print('6. Enviar mensaje directo'),
            print('7. Ingresar a una conversación grupal'),
            print('8. Enviar mensaje a un grupo'),
            print('9. Definir mensaje de presencia'),
            print('10. Enviar archivo')
            menu = int(input('Ingrese el numero de la opcion que desea: '))

            if menu == 2:
                client.deleteUser()
                menu = 1

            elif menu == 1:
                client.disconnect()
                logged = False

            elif menu == 3:
                print(client.getUsers())

            elif menu == 4:
                client.addUser()
            
            elif menu == 5:
                print(client.userInfo())

            elif menu == 6:
                client.send_msg()

            elif menu == 7:
                client.joinRoom()

            elif menu == 8:
                client.sendMessageToRoom()

            elif menu == 9:
                client.changePresence()
            
            elif menu == 10:
                client.sendFile()
            
            else:
                print('Seleccione una opcion valida. \n')
                









        


        