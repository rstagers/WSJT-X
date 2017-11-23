# Header class for all WSJT received packets.  This class handles the header and 
# will create class for handling the packet depending on the packet type in  
# the header.  
import struct

class WSJTX_Packet():

    def __init__(self, pkt, idx):
        self.index = idx            # Keeps track of where we are in the packet parsing!
        self.packet = pkt
        self.MagicNumber = 0
        self.SchemaVersion = 0
        self.PacketType = 0
        self.ClientID = ""
    
    # Methods to extract the different types of data in the packet.  These are shared with all 
    # the other packet classes.

    # read a utf8 string.  a 32bit length followed by the data.  -1 is no data present.
    # updates __index and returns a string. 
    def readutf8(self):
        strLength = self.getInt32()
        # BUG BUG what happens if strlength is zero?
        if strLength > 0:
            stringRead = struct.unpack(">"+str(strLength)+"s", self.packet[self.index:strLength+self.index])
            self.index += strLength
            return (stringRead[0].decode('utf-8'))
        else:
            return ("")

    # read a bool value.  Updates __index. Returns the bool value True or False

    def getDateTime(self):
        TimeOffset = 0
        DateOff = self.getLongLong()        
        TimeOff = self.getuInt32()        
        TimeSpec = self.getByte()
        if TimeSpec == 2:
            TimeOffset = self.getInt32()
        return (DateOff, TimeOff, TimeSpec, TimeOffset)

    def getByte(self):
        data = struct.unpack(">B", self.packet[self.index:self.index+1])
        self.index += 1
        return data[0]

    def getBool(self):
        data = struct.unpack(">?", self.packet[self.index:self.index+1])
        self.index += 1
        return data[0]

    # read a In32 value.  Updates __index. Returns the Int32 value
    def getInt32(self):
        data = struct.unpack(">i", self.packet[self.index:self.index+4])
        self.index += 4
        return data[0]

    # read a unsigned Int32 value.  Updates __index. Returns the iInt32 value
    def getuInt32(self):
        data = struct.unpack(">I", self.packet[self.index:self.index+4])
        self.index += 4
        return data[0]

    # read a longlong value.  Updates __index. Returns the longlong value 
    def getLongLong(self):
        data = struct.unpack(">Q", self.packet[self.index:self.index+8])
        self.index += 8
        return data[0]

    def getDouble(self):
        data = struct.unpack(">d", self.packet[self.index:self.index+8])
        self.index += 8
        return data[0]

    def Decode(self):
    # in here depending on the Packet Type we creat the class to handle the packet!
        self.MagicNumber = self.getuInt32()
        self.SchemaVersion = self.getuInt32()
        self.PacketType = self.getuInt32()
        self.ClientID = self.readutf8()

# 00000220:           adbc cbda 0000 0002 0000 0000      ............
# 00000230: 0000 0006 5753 4a54 2d58 0000 0003 0000  ....WSJT-X......
# 00000240: 0005 312e 382e 3000 0000 0572 3831 3933  ..1.8.0....r8193

# Packet Type 0 Heartbeat
# The heartbeat  message shall be  sent on a periodic  basis every
# NetworkMessage::pulse   seconds   (see    below),   the   WSJT-X
# application  does  that  using the  MessageClient  class.   This
# message is intended to be used by servers to detect the presence
# of a  client and also  the unexpected disappearance of  a client
# and  by clients  to learn  the schema  negotiated by  the server
# after it receives  the initial heartbeat message  from a client.
# The message_aggregator reference server does just that using the
# MessageServer class. Upon  initial startup a client  must send a
# heartbeat message as soon as  is practical, this message is used
# to negotiate the maximum schema  number common to the client and
# server. Note  that the  server may  not be  able to  support the
# client's  requested maximum  schema  number, in  which case  the
# first  message received  from the  server will  specify a  lower
# schema number (never a higher one  as that is not allowed). If a
# server replies  with a lower  schema number then no  higher than
# that number shall be used for all further outgoing messages from
# either clients or the server itself.

# Note: the  "Maximum schema number"  field was introduced  at the
# same time as schema 3, therefore servers and clients must assume
# schema 2 is the highest schema number supported if the Heartbeat
# message does not contain the "Maximum schema number" field.

class WSJTX_Heartbeat(WSJTX_Packet):

    def __init__(self, pkt, idx):
        WSJTX_Packet.__init__(self, pkt, idx)
        self.MaximumSchema = 0
        self.Version = ""
        self.Revision = ""

    def Decode(self):
        self.MaximumSchema = self.getuInt32()
        self.Version = self.readutf8()
        self.Revision = self.readutf8()


# 00000000: adbc cbda 0000 0002 0000 0001 0000 0006  ................
# 00000010: 5753 4a54 2d58 0000 0000 00d6 c090 0000  WSJT-X..........
# 00000020: 0003 4654 3800 0000 044b 4232 4d00 0000  ..FT8....KB2M...
# 00000030: 032d 3135 0000 0003 4654 3800 0001 0000  .-15....FT8.....
# 00000040: 03a4 0000 03a4 0000 0004 4b39 5644 0000  ..........K9VD..
# 00000050: 0006 434e 3837 7878 0000 0004 454c 3939  ..CN87xx....EL99
# 00000060: 00ff ffff ff00

# Packet Type 1 Status
# WSJT-X  sends this  status message  when various  internal state
# changes to allow the server to  track the relevant state of each
# client without the need for  polling commands. The current state
# changes that generate status messages are:

#      Application start up,
#      "Enable Tx" button status changes,
#      Dial frequency changes,
#      Changes to the "DX Call" field,
#      Operating mode, sub-mode or fast mode changes,
#      Transmit mode changed (in dual JT9+JT65 mode),
#      Changes to the "Rpt" spinner,
#      After an old decodes replay sequence (see Replay below),
#      When switching between Tx and Rx mode,
#      At the start and end of decoding,
#      When the Rx DF changes,
#      When the Tx DF changes,
#      When the DE call or grid changes (currently when settings are exited),
#      When the DX call or grid changes,
#      When the Tx watchdog is set or reset.

class WSJTX_Status(WSJTX_Packet):

    def __init__(self, pkt, idx):
        WSJTX_Packet.__init__(self, pkt, idx)
        self.Frequency = 0
        self.Mode = ""
        self.DXCall = ""
        self.Report = ""
        self.TxMode = ""
        self.TxEnabled = False
        self.Transmitting = False
        self.Decoding = False
        self.RxDF = 0
        self.TxDF = 0
        self.DECall = ""
        self.DEgrid = ""
        self.DXgrid = ""
        self.TxWatchdog = False
        self.Submode = ""
        self.Fastmode = False

    def Decode(self):
        self.Frequency = self.getLongLong()     
        self.Mode = self.readutf8()
        self.DXCall = self.readutf8()
        self.Report = self.readutf8()
        self.TxMode = self.readutf8()
        self.TxEnabled = self.getBool()
        self.Transmitting = self.getBool()
        self.Decoding = self.getBool()
        self.RxDF = self.getuInt32()
        self.TxDF = self.getuInt32()
        self.DECall = self.readutf8()
        self.DEgrid = self.readutf8()
        self.DXgrid = self.readutf8()
        self.TxWatchdog = self.getBool()
        self.Submode = self.readutf8()
        self.Fastmode = self.getBool()


'''
 New                    bool
 Time                   QTime (quint32)
 snr                    qint32
 Delta time (S)         float (serialized as double) (8 bytes)
 Delta frequency (Hz)   quint32
 Mode                   utf8
 Message                utf8
 Low confidence         bool
 Off air                bool
'''

# 00000060               adbc cbda 0000 0002 0000        ..........
# 00000070: 0002 0000 0006 5753 4a54 2d58 0104 5b1c  ......WSJT-X..[.
# 00000080: c0ff ffff e83f b999 99a0 0000 0000 0001  .....?..........
# 00000090: 5400 0000 017e 0000 000e 4351 204b 4134  T....~....CQ KA4
# 000000a0: 484f 5420 454d 3634 0000                   HOT EM64

# Packet Type 2
# The decode message is sent when  a new decode is completed, in
# this case the 'New' field is true. It is also used in response
# to  a "Replay"  message where  each  old decode  in the  "Band
# activity" window, that  has not been erased, is  sent in order
# as a one of these messages  with the 'New' field set to false.
# See  the "Replay"  message below  for details  of usage.   Low
# confidence decodes are flagged  in protocols where the decoder
# has knows that  a decode has a higher  than normal probability
# of  being  false, they  should  not  be reported  on  publicly
# accessible services  without some attached warning  or further
# validation. Off air decodes are those that result from playing
# back a .WAV file.

class WSJTX_Decode(WSJTX_Packet):

    def __init__(self, pkt, idx):
        WSJTX_Packet.__init__(self, pkt, idx)
        New = False
        Time = 0
        snr = 0
        DeltaTime = 0.0
        DeltaFrequency = 0  # BUG BUG Guessing here, order could be swapped. check when actually run!
        Mode = ""
        Message = ""
        LowConfidence = False
        OffAir = False

    def Decode(self):
        self.New = self.getBool()
        self.Time = self.getuInt32()
        self.snr = self.getInt32()
        self.DeltaTime = self.getDouble()
        self.DeltaFrequency = self.getuInt32()
        self.Mode = self.readutf8()
        self.Message = self.readutf8()
        self.LowConfidence = self.getBool()
        self.OffAir = self.getBool()


# Packet Type 3
# This message is sent  when all prior "Decode"  messages in the
# "Band activity"  window have been discarded  and therefore are
# no long available for actioning  with a "Reply" message. It is
# sent when the user erases  the "Band activity" window and when
# WSJT-X  closes down  normally. The  server should  discard all
# decode messages upon receipt of this message.

class WSJTX_Erase(WSJTX_Packet):

    def __init__(self, pkt, idx):
        WSJTX_Packet.__init__(self, pkt, idx)

# Packet Type 4 Reply IN message to client
# In order for a server  to provide a useful cooperative service
# to WSJT-X it  is possible for it to initiate  a QSO by sending
# this message to a client. WSJT-X filters this message and only
# acts upon it  if the message exactly describes  a prior decode
# and that decode  is a CQ or QRZ message.   The action taken is
# exactly equivalent to the user  double clicking the message in
# the "Band activity" window. The  intent of this message is for
# servers to be able to provide an advanced look up of potential
# QSO partners, for example determining if they have been worked
# before  or if  working them  may advance  some objective  like
# award progress.  The  intention is not to  provide a secondary
# user  interface for  WSJT-X,  it is  expected  that after  QSO
# initiation the rest  of the QSO is carried  out manually using
# the normal WSJT-X user interface.
#
# The  Modifiers   field  allows  the  equivalent   of  keyboard
# modifiers to be sent "as if" those modifier keys where pressed
# while  double-clicking  the  specified  decoded  message.  The
# modifier values (hexadecimal) are as follows:
# 
#      no modifier     0x00
#      SHIFT           0x02
#      CTRL            0x04  CMD on Mac
#      ALT             0x08
#      META            0x10  Windows key on MS Windows
#      KEYPAD          0x20  Keypad or arrows
#      Group switch    0x40  X11 only

class WSJTX_Reply(WSJTX_Packet):

    def __init__(self, pkt, idx):
        WSJTX_Packet.__init__(self, pkt, idx)



# 00000000: adbc cbda 0000 0002 0000 0005 0000 0006  ................
# 00000010: 5753 4a54 2d58 0000 0000 0025 81da 0476  WSJT-X.....%...v
# 00000020: cf08 0000 0000 0557 4c37 4347 0000 0004  .......WL7CG....
# 00000030: 4250 3631 0000 0000 00d6 c358 0000 0003  BP61.......X....
# 00000040: 4654 3800 0000 032d 3134 0000 0003 2d31  FT8....-14....-1
# 00000050: 3500 0000 0000 0000 0000 0000 0000 0000  5...............
# 00000060: 0000 2581 da04 761f 3500                 ..%...v.5.
# Date & Time Off        QDateTime
# DX call                utf8
# DX grid                utf8
# Dial frequency (Hz)    quint64
# Mode                   utf8
# Report send            utf8
# Report received        utf8
# Tx power               utf8
# Comments               utf8
# Name                   utf8
# Date & Time On         QDateTime


#*      QDateTime:
# *     8      QDate      qint64    Julian day number
# *     4      QTime      quint32   Milli-seconds since midnight
# *     1      timespec   quint8    0=local, 1=UTC, 2=Offset from UTC
# *                                                 (seconds)
# *                                3=time zone
# *     4     offset     qint32    only present if timespec=2
# *           timezone   several-fields only present if timespec=3

# Packet Type 5 QSO Logged
# The  QSO logged  message is  sent  to the  server(s) when  the
# WSJT-X user accepts the "Log  QSO" dialog by clicking the "OK"
# button.

class WSJTX_Logged(WSJTX_Packet):

    def __init__(self, pkt, idx):
        WSJTX_Packet.__init__(self, pkt, idx)
        self.DateOff = 0 
        self.TimeOff = 0
        self.TimeOffSpec = 0
        self.TimeOffOffset = 0       
        self.DXcall = ""
        self.DXgrid = ""
        self.DialFrequency = 0
        self.Mode = ""
        self.ReportSent = ""
        self.ReportReceived = ""
        self.TxPower = ""
        self.Comments = ""
        self.Name = ""
        self.DateOn = 0
        self.TimeOn = 0
        self.TimeOnSpec = 0
        self.TimeOnOffset = 0

    def Decode(self):
        DTTuple = self.getDateTime()
        self.DateOff = DTTuple[0]
        self.TimeOff = DTTuple[1]
        self.TimeOffSpec = DTTuple[2]
        self.TimeOffOffset = DTTuple[3]
        self.DXcall = self.readutf8()
        self.DXgrid = self.readutf8()
        self.DialFrequency = self.getLongLong()
        self.Mode = self.readutf8()
        self.ReportSent = self.readutf8()
        self.ReportReceived = self.readutf8()
        self.TxPower = self.readutf8()
        self.Comments = self.readutf8()
        self.Name = self.readutf8()
        DTTuple = self.getDateTime()
        self.DateOn = DTTuple[0]
        self.TimeOn = DTTuple[1]
        self.TimeOnSpec = DTTuple[2]
        self.TimeOnOffset = DTTuple[3]

# Packet Type 6 Close
# Close is sent by a client immediately prior to it shutting
# down gracefully.
class WSJTX_Closed(WSJTX_Packet):

    def __init__(self, pkt, idx):
        WSJTX_Packet.__init__(self, pkt, idx)

# Packet Type 7 Replay (IN to client This is a message to be sent to the client)
#
# When a server starts it may  be useful for it to determine the
# state  of preexisting  clients. Sending  this message  to each
# client as it is discovered  will cause that client (WSJT-X) to
# send a "Decode" message for each decode currently in its "Band
# activity"  window. Each  "Decode" message  sent will  have the
# "New" flag set to false so that they can be distinguished from
# new decodes. After  all the old decodes have  been broadcast \
# "Status" message  is also broadcast.  If the server  wishes to
# determine  the  status  of  a newly  discovered  client;  this
# message should be used.
class WSJTX_Replay(WSJTX_Packet):

    def __init__(self, pkt, idx):
        WSJTX_Packet.__init__(self, pkt, idx)

# Packet Type 8 Halt Tx (IN to client This is a message to be sent to the client)
#
# The server may stop a client from transmitting messages either
# immediately or at  the end of the  current transmission period
# using this message.

class WSJTX_HaltTx(WSJTX_Packet):

    def __init__(self, pkt, idx):
        WSJTX_Packet.__init__(self, pkt, idx)

# Packet Type 9 (IN to client This is a message to be sent to the client)
#
# This message  allows the server  to set the current  free text
# message content. Sending this  message with a non-empty "Text"
# field is equivalent to typing  a new message (old contents are
# discarded) in to  the WSJT-X free text message  field or "Tx5"
# field (both  are updated) and if  the "Send" flag is  set then
# clicking the "Now" radio button for the "Tx5" field if tab one
# is current or clicking the "Free  msg" radio button if tab two
# is current.
#
# It is the responsibility of the  sender to limit the length of
# the  message   text  and   to  limit   it  to   legal  message
# characters. Despite this,  it may be difficult  for the sender
# to determine the maximum message length without reimplementing
# the complete message encoding protocol. Because of this is may
# be better  to allow any  reasonable message length and  to let
# the WSJT-X application encode and possibly truncate the actual
# on-air message.

# If the  message text is  empty the  meaning of the  message is
# refined  to send  the  current free  text  unchanged when  the
# "Send" flag is set or to  clear the current free text when the
# "Send" flag is  unset.  Note that this API does  not include a
# command to  determine the  contents of  the current  free text
# message.

class WSJTX_FreeText(WSJTX_Packet):

    def __init__(self, pkt, idx):
        WSJTX_Packet.__init__(self, pkt, idx)

# Packet Type 10 WSPR Decode

# The decode message is sent when  a new decode is completed, in
# this case the 'New' field is true. It is also used in response
# to  a "Replay"  message where  each  old decode  in the  "Band
# activity" window, that  has not been erased, is  sent in order
# as  a one  of  these  messages with  the  'New'  field set  to
# false.  See   the  "Replay"  message  below   for  details  of
# usage. The off air field indicates that the decode was decoded
# from a played back recording.

class WSJTX_WSPRDecode(WSJTX_Packet):

    def __init__(self, pkt, idx):
        WSJTX_Packet.__init__(self, pkt, idx)



