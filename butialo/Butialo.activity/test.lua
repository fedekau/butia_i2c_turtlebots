--wait(1)

for nombre, d in pairs(devices) do
	print (nombre)
end

local mensaje="oioioi!"
print("Enviando:", mensaje)
Lback.send(mensaje)
print("Leyendo:", Lback.read())
