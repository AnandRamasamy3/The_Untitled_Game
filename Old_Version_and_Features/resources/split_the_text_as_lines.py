message="Anand Ramasamy is my name and I'm from Dharmapuri studying in Governemnt college of Engineering Dharmapuri in the field of Computer Science and Engineering"
message="fine dude...!!! doing good what are you doing ?"
result=[""]

length=26

message=message.split(" ",)

while len(message)>0:
    print (message,result)
    if len(result[-1])<length:
        if (len(result[-1])+len(message[0]))<length:
            result[-1]+=" "+message[0]
            message.remove(message[0])
        elif len(result[-1])<(length/2):
            rem_length=length-len(result[-1])-1
            result[-1]+=" "+message[0][0:rem_length]
            message[0]=message[0].replace(message[0][0:rem_length],"")
        else:
            result.append("")
    else:
        result.append("")
    print (message,result)


for i in result:
    print (i,"===",len(i))
