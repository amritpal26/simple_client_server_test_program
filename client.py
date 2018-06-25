import socket, json, time
import random as random_timing
import random as random_corrupt
import random


seed_timing = 0
num_packets = 0
seed_corrupt = 0
corrupt_probablity = 0

rdt_send_called = None
rcvpkt = None
expected_arrival_time = 0
back = False


# states = {"WAIT FOR CALL 0 FROM ABOVE", "WAIT FOR CALL 0 FROM ABOVE"}

wait_for_ack_or_nack = None
wait_for_call_0 = True
wait_for_call_1 = True

serverName = 'localhost'
serverPort = 50008

senderSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
packetsSent = 0

packet = None

def main():
	seed_timing = float(input ("The seed for the random number generator used for timing: "))
	num_packets = int(input ("Number of packets to send: "))
	seed_corrupt =  float(input ("The seed for the random number generator used for used for determining if ACKs or NACKshave been corrupted: "))
	corrupt_probablity = float(input ("The probability that an ACK or NACK has been corrupted: "))

	random_timing.seed(seed_timing)
	random_corrupt.seed(seed_corrupt)

	global expected_arrival_time, back, packetsSent

	while packetsSent < num_packets:
		if (back != True):
			print("The sender is moving to state WAIT FOR CALL 0 FROM ABOVE")
		else:
			print("The sender is moving back to state WAIT FOR CALL 0 FROM ABOVE")

		dataToSend = random.randint(1, 500)
		while expected_arrival_time > time.time():
			pass
		expected_arrival_time = time.time() + random_timing.randint(1,6)

		data = rdt_send(dataToSend)
		sndpkt = make_pkt(data, False, False, False)
		print("A packet with sequence number 0 is about to be sent")
		udt_send(sndpkt)

		if (not back):
			print("The sender is moving to state WAIT FOR ACK OR NACK 0")
		else:
			print("The sender is moving back to state WAIT FOR ACK OR NACK 0")


		fail = True
		while (fail):
			while(not rdt_rcv()):
				pass
			global rcvpkt
			content1 = str(rcvpkt['content'])
			seq_num1 = str(int(rcvpkt['seq_num']))
			ack1 = str(int(rcvpkt['ack']))
			nack1 = str(int(rcvpkt['nack']))

			if isCorrupt(rcvpkt) == True:
				print("A Corrupted ACK or NACK packet has just been received")
				print("A packet with sequence number 0 is about to be resent")
				udt_send(sndpkt)

			elif isNack(rcvpkt) == True:
				print("A NACK packet has just been received")
				print("Packet received contains: data = " + content1 + " seq = " + seq_num1 + " ack = " + ack1 + " nack = " + nack1)
				print("A packet with sequence number 0 is about to be resent")
				udt_send(sndpkt)


			elif isAck(rcvpkt) == True:
				fail = False

				packetsSent = packetsSent + 1
				if packetsSent >= num_packets:
					break

				print("An ACK packet has just been received")
				if back == True:
					print("The sender is moving to state WAIT FOR CALL 1 FROM ABOVE")
				else:
					print("The sender is moving back to state WAIT FOR CALL 1 FROM ABOVE")

				

				dataToSend = random.randint(1, 500)
				while expected_arrival_time > time.time():
					pass
				expected_arrival_time = time.time() + random_timing.randint(1,6)

				data = rdt_send(dataToSend)
				sndpkt = make_pkt(data, True, False, False)
				print("A packet with sequence number 1 is about to be sent")
				udt_send(sndpkt)

				if (not back):
					print("The sender is moving to state WAIT FOR ACK OR NACK 1")
				else:
					print("The sender is moving back to state WAIT FOR ACK OR NACK 1")


				fail = True
				while (fail):
					while(not rdt_rcv()):
						pass

					content1 = str(rcvpkt['content'])
					seq_num1 = str(int(rcvpkt['seq_num']))
					ack1 = str(int(rcvpkt['ack']))
					nack1 = str(int(rcvpkt['nack']))
						
					if isCorrupt(rcvpkt) == True:
						print("A Corrupted ACK or NACK packet has just been received")
						print("A packet with sequence number 1 is about to be resent")
						udt_send(sndpkt)

					elif isNack(rcvpkt) == True:
						print("A NACK packet has just been received")
						print("Packet received contains: data = " + content1 + " seq = " + seq_num1 + " ack = " + ack1 + " nack = " + nack1)
						print("A packet with sequence number 1 is about to be resent")
						udt_send(sndpkt)


					elif isAck(rcvpkt) == True:
						fail = False
						back = True
						packetsSent += 1
						print("An ACK packet has just been received")
						if packetsSent >= num_packets:
							break


	senderSocket.close()
	return


def make_pkt(content, seq_num, ack, nack):
	packetDict = {'content': content, 'seq_num': seq_num, 'ack': ack, 'nack': nack}
	packet = json.dumps(packetDict)
	return packet

def rdt_send(data):
	data = random.randint(1, 500)
	return data

def udt_send(sndpkt):
	senderSocket.sendto(sndpkt.encode(), (serverName, serverPort))

def rdt_rcv():
	recievedPacket, recieverAddress = senderSocket.recvfrom(2048)
	recievedPacket = recievedPacket.decode('utf-8')
	if recievedPacket:
		packetDict = json.loads(recievedPacket)
		global rcvpkt
		rcvpkt = packetDict
		return rcvpkt
	else:
		return False

def isAck(packet):
	if packet['ack'] == True:
		return True
	else:
		return False

def isNack(packet):
	if packet['nack'] == True:
		return True
	else:
		return False

def isCorrupt(packet):
	randomNum = random.random()
	if randomNum < corrupt_probablity:
		return True
	else:
		return False


if __name__ == '__main__':
	main()
