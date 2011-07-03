require 'butialo'--; setfenv(1,_G)

--local event=require "event"


local function p1(v)
 print (">",v)
end 
local function p2(v)
 print ("<",v)
end 
local function p3(v)
 print ("!",v)
 event.stop()
end 
print(p1,p2)
event.add( Pote.get_pote, ">", 200,  p1 )
event.add( Pote.get_pote, "<", 200,  p2 )
event.add( Pote.get_pote, "<", 2,  p3 )
event.go()
print("Fin!")
