require "butialo"

--wait(1)

for nombre, d in pairs(DEVICES) do
	print (nombre)
end

mensaje="oioioi!"
print("Enviando:", mensaje)
Lback.send(mensaje)
print("Leyendo:", Lback.read())
