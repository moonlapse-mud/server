from moonlapseshared.packet import *


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
        self.protocol.send_packet(OkPacket())
        pass

    def handle_register_packet(self, p: RegisterPacket):
        pass

