from django.core.exceptions import ObjectDoesNotExist
from moonlapseshared.packet import *
from . import models
from . import pbkdf2


class ProtoState:
    def __init__(self, protocol):
        self.protocol = protocol

        # would like to factor this out so it isn't created on each new ProtoState
        self.statemap = {
            OkPacket: self.handle_ok_packet,
            RegisterPacket: self.handle_register_packet,
            LoginPacket: self.handle_login_packet
        }

    def dispatch_packet(self, p: Packet):
        try:
            self.statemap[type(p)](p)
        except NotImplementedError:
            print(f"Packet ({p.__class__.__name__}) not registered in this state ({self.__class__.__name__})")

    def handle_ok_packet(self, p: OkPacket):
        raise NotImplementedError()

    def handle_register_packet(self, p: RegisterPacket):
        raise NotImplementedError()

    def handle_login_packet(self, p: LoginPacket):
        raise NotImplementedError()


class EntryState(ProtoState):
    def __init__(self, protocol):
        super().__init__(protocol)

    def handle_login_packet(self, p: LoginPacket):
        print("attempting to login")
        username = ~p.username
        password = ~p.password

        if not models.User.objects.filter(username=username):
            self.protocol.outgoing.append(DenyPacket(DenyPacket.LOGIN_PLAYER_DOESNT_EXIST))
            return

        user = models.User.objects.get(username=username)
        player = models.Player.objects.get(user=user)

        # if self.server.is_logged_in(player.pk):
        #     self.outgoing.append(packet.DenyPacket(f"{username} is already inhabiting this realm."))
        #     return

        if not pbkdf2.verify_password(user.password, password):
            self.protocol.outgoing.append(DenyPacket(DenyPacket.LOGIN_INCORRECT_PASSWORD))
            return

        # The user exists in the database so retrieve the player and entity objects
        # self.username = user.username
        # self.player_info = player
        # self.player_instance = models.InstancedEntity.objects.get(entity=self.player_info.entity)
        # self.player_instance = self.server.instances[self.player_instance.pk]

        self.protocol.outgoing.append(OkPacket())
        # self.move_rooms(self.player_instance.room.id)

    def handle_register_packet(self, p: RegisterPacket):
        username = ~p.username

        if models.User.objects.filter(username=username):
            self.protocol.outgoing.append(DenyPacket(DenyPacket.REGISTER_PLAYER_ALREADY_EXISTS))
            return

        password = pbkdf2.hash_password(~p.password)

        # save new user
        user = models.User(username=username, password=password)
        try:
            user.save()
        except Exception as e:
            print(f"Error saving user. {e}")
            self.protocol.outgoing.append(DenyPacket(DenyPacket.REGISTER_TOO_LONG))
            return

        # create and save new entity
        entity = models.Entity(typename='Player', name=username)
        entity.save()

        # Create and save a new instance
        initial_room = models.Room.objects.first()
        if not initial_room:
            raise ObjectDoesNotExist("Initial room not loaded. Did you run loaddata.py?")
        instance = models.InstancedEntity(entity=entity, room=initial_room, y=0, x=0)
        instance.save()

        # Create and save a new container (inventory)
        container = models.Container()
        container.save()

        # Create and save a new player
        player = models.Player(user=user, entity=entity, inventory=container)
        player.save()

        # adding instance to server
        # todo: this
        # self.protocol.server.instances[instance.pk] = instance

        self.protocol.outgoing.append(OkPacket())
