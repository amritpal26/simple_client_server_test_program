import socket, json, time
import random

corrupt_probablity = None
seed_for_random = None

serverName = 'localhost'
serverPort = 50008
senderAddress = None

previousPacketForIsCorrupt = None
previousResultForIsCorrupt = None

lastPacketReceivedSeq = 1
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)	
serverSocket.bind((serverName, serverPort))

rcvpkt = None
dataReceived = 0
previousReceivedPacket = None

def main():
	global corrupt_probablity, seed_for_random,	serverSocket, rcvpkt,lastPacketReceivedSeq, dataReceived
	corrupt_probablity = float(input("Enter the probability of Ack or Nack being corrupt: "))
	seed_for_random = float(input("Enter the seed for random number generator used for determining if ACKs or NACKs have been corrupted: "))

	random.seed(seed_for_random)

	print("The receiver is moving to state WAIT FOR 0 FROM BELOW")
	while True:

		while True:
			rdt_rcv()
			iscorrupt = isCorrupt(rcvpkt)
			receiveDone = False
			content1 = str(rcvpkt['content'])
			seq_num1 = str(int(rcvpkt['seq_num']))
			ack1 = str(int(rcvpkt['ack']))
			nack1 = str(int(rcvpkt['nack']))


			if ((iscorrupt == False) and (hasSeq0(rcvpkt)) and (receiveDone == False)):
				if lastPacketReceivedSeq == 1:
					print("A packet with sequence number 0 has been received")
					print("Packet received contains: data = " + content1 + " seq = " + seq_num1 + " ack = " + ack1 + " nack = " + nack1)
					dataReceived +=1
					lastPacketReceivedSeq = 0
					deliver_data(content1)

					sndpkt = make_pkt(0, 0, 1, 0)
					udt_send(sndpkt)

					if(dataReceived > 1):
						print("The receiver is moving back to state WAIT FOR 1 FROM BELOW")
					else:
						print("The receiver is moving to state WAIT FOR 1 FROM BELOW")
				
				elif lastPacketReceivedSeq == 0:
					print("A duplicate packet with sequence number 0 has been received")
					print("Packet received contains: data = " + content1 + " seq = " + seq_num1 + " ack = " + ack1 + " nack = " + nack1)
					sndpkt = make_pkt(0, 0, 1, 0)
					udt_send(sndpkt)

				receiveDone = True

			if ((iscorrupt == False) and (hasSeq1(rcvpkt)) and (receiveDone == False)):
				if lastPacketReceivedSeq == 0:
					print("A packet with sequence number 1 has been received")
					print("Packet received contains: data = " + content1 + " seq = " + seq_num1 + " ack = " + ack1 + " nack = " + nack1)
					dataReceived += 1
					lastPacketReceivedSeq = 1
					deliver_data(content1)

					sndpkt = make_pkt(0, 1, 1, 0)
					udt_send(sndpkt)

					if(dataReceived > 1):
						print("The receiver is moving back to state WAIT FOR 0 FROM BELOW")
					else:
						print("The receiver is moving to state WAIT FOR 0 FROM BELOW")
				
				elif lastPacketReceivedSeq == 1:
					print("A duplicate packet with sequence number 1 has been received")
					print("Packet received contains: data = " + content1 + " seq = " + seq_num1 + " ack = " + ack1 + " nack = " + nack1)
					sndpkt = make_pkt(0, 1, 1, 0)
					udt_send(sndpkt)

				receiveDone = True

			
			if (iscorrupt != False):
				print("A Corrupted packet has just been received")
				sndpkt = make_pkt(0, 0, 0, 1)
				udt_send(sndpkt)

	serverSocket.close()
	return
			



def make_pkt(content, seq_num, ack, nack):
	packetDict = {'content': content, 'seq_num': seq_num, 'ack': ack, 'nack': nack}
	packet = json.dumps(packetDict)
	return packet

def udt_send(sndpkt):
	serverSocket.sendto(sndpkt.encode(), senderAddress)

def rdt_rcv():
	global serverSocket, rcvpkt, senderAddress, previousReceivedPacket
	recievedPacket, senderAddress =	serverSocket.recvfrom(2048)
	if (recievedPacket != previousReceivedPacket) or (previousReceivedPacket == None):
		packetDict = json.loads(recievedPacket)
		previousReceivedPacket = recievedPacket
		rcvpkt = packetDict
		return rcvpkt
	else: 
		return False

def isCorrupt(packet):
	randomNum = random.random()
	if randomNum < corrupt_probablity:
		previousResultForIsCorrupt = True
		return True
	else:
		previousPacketForIsCorrupt = False
		return False


def hasSeq0(packet):
	return packet['seq_num'] == 0

def hasSeq1(packet):
	return packet['seq_num'] == 1

def deliver_data(data):
	pass


if __name__ == '__main__':
	main()
