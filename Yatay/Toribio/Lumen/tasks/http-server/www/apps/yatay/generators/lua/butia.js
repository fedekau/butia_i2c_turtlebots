/* Automatically Generated Code */
'use strict';

goog.provide('Blockly.Lua.butia');
goog.require('Blockly.Lua');

Blockly.Lua['mover adelante'] = function(block) { 
	var debugTrace = ''; 
	var params = String("Yatay.vel,-Yatay.vel").replace(/Yatay.vel/g, String(Yatay.vel)); 
	return debugTrace + "robot.execute('butia_skid','set_vel',{" + params + "}, M.userId)\n "; 
}; 

Blockly.Lua['mover atras'] = function(block) { 
	var debugTrace = ''; 
	var params = String("-Yatay.vel,Yatay.vel").replace(/Yatay.vel/g, String(Yatay.vel)); 
	return debugTrace + "robot.execute('butia_skid','set_vel',{" + params + "}, M.userId)\n "; 
}; 

Blockly.Lua['detener'] = function(block) { 
	var debugTrace = ''; 
	var params = String("0,0").replace(/Yatay.vel/g, String(Yatay.vel)); 
	return debugTrace + "robot.execute('butia_skid','set_vel',{" + params + "}, M.userId)\n "; 
}; 

Blockly.Lua['girar derecha'] = function(block) { 
	var debugTrace = ''; 
	var params = String("-Yatay.vel,-Yatay.vel").replace(/Yatay.vel/g, String(Yatay.vel)); 
	return debugTrace + "robot.execute('butia_skid','set_vel',{" + params + "}, M.userId)\n "; 
}; 

Blockly.Lua['girar izquierda'] = function(block) { 
	var debugTrace = ''; 
	var params = String("Yatay.vel,Yatay.vel").replace(/Yatay.vel/g, String(Yatay.vel)); 
	return debugTrace + "robot.execute('butia_skid','set_vel',{" + params + "}, M.userId)\n "; 
}; 

Blockly.Lua['mover'] = function(block) { 
	var debugTrace = ''; 
	var arg1 = Blockly.Lua.statementToCode(block, '1') || '0'; 
	var arg2 = Blockly.Lua.statementToCode(block, '2') || '0'; 
	var params = String(arg1 + "," + arg2).replace(/Yatay.vel/g, String(Yatay.vel)); 
	return debugTrace + "robot.execute('butia_skid','set_vel',{" + params + "}, M.userId)\n "; 
}; 

Blockly.Lua['distance. (5)'] = function(block) { 
	var debugTrace = ''; 
	var params = String().replace(/Yatay.vel/g, String(Yatay.vel)); 
	return debugTrace + "robot.execute('bb-distanc:5','getValue',{" + params + "}, M.userId)\n "; 
}; 

Blockly.Lua['grey (2)'] = function(block) { 
	var debugTrace = ''; 
	var params = String().replace(/Yatay.vel/g, String(Yatay.vel)); 
	return debugTrace + "robot.execute('bb-grey:2','getValue',{" + params + "}, M.userId)\n "; 
}; 

Blockly.Lua['grey (3)'] = function(block) { 
	var debugTrace = ''; 
	var params = String().replace(/Yatay.vel/g, String(Yatay.vel)); 
	return debugTrace + "robot.execute('bb-grey:3','getValue',{" + params + "}, M.userId)\n "; 
}; 

Blockly.Lua['move forward'] = function(block) { 
	var debugTrace = ''; 
	if (Yatay.DebugMode) { 
		debugTrace = "robot.put_debug_result('"+ block.id +"', M.userId)\n"; 
	} 
	var params = String("Yatay.vel,-Yatay.vel").replace(/Yatay.vel/g, String(Yatay.vel)); 
	return debugTrace + "robot.execute('butia_skid','set_vel',{" + params + "}, M.userId)\n "; 
}; 

Blockly.Lua['move back'] = function(block) { 
	var debugTrace = ''; 
	if (Yatay.DebugMode) { 
		debugTrace = "robot.put_debug_result('"+ block.id +"', M.userId)\n"; 
	} 
	var params = String("-Yatay.vel,Yatay.vel").replace(/Yatay.vel/g, String(Yatay.vel)); 
	return debugTrace + "robot.execute('butia_skid','set_vel',{" + params + "}, M.userId)\n "; 
}; 

Blockly.Lua['stop'] = function(block) { 
	var debugTrace = ''; 
	if (Yatay.DebugMode) { 
		debugTrace = "robot.put_debug_result('"+ block.id +"', M.userId)\n"; 
	} 
	var params = String("0,0").replace(/Yatay.vel/g, String(Yatay.vel)); 
	return debugTrace + "robot.execute('butia_skid','set_vel',{" + params + "}, M.userId)\n "; 
}; 

Blockly.Lua['turn right'] = function(block) { 
	var debugTrace = ''; 
	if (Yatay.DebugMode) { 
		debugTrace = "robot.put_debug_result('"+ block.id +"', M.userId)\n"; 
	} 
	var params = String("-Yatay.vel,-Yatay.vel").replace(/Yatay.vel/g, String(Yatay.vel)); 
	return debugTrace + "robot.execute('butia_skid','set_vel',{" + params + "}, M.userId)\n "; 
}; 

Blockly.Lua['turn left'] = function(block) { 
	var debugTrace = ''; 
	if (Yatay.DebugMode) { 
		debugTrace = "robot.put_debug_result('"+ block.id +"', M.userId)\n"; 
	} 
	var params = String("Yatay.vel,Yatay.vel").replace(/Yatay.vel/g, String(Yatay.vel)); 
	return debugTrace + "robot.execute('butia_skid','set_vel',{" + params + "}, M.userId)\n "; 
}; 

Blockly.Lua['move'] = function(block) { 
	var debugTrace = ''; 
	if (Yatay.DebugMode) { 
		debugTrace = "robot.put_debug_result('"+ block.id +"', M.userId)\n"; 
	} 
	var arg1 = Blockly.Lua.statementToCode(block, '1') || '0'; 
	var arg2 = Blockly.Lua.statementToCode(block, '2') || '0'; 
	var params = String(arg1 + "," + arg2).replace(/Yatay.vel/g, String(Yatay.vel)); 
	return debugTrace + "robot.execute('butia_skid','set_vel_2',{" + params + "}, M.userId)\n "; 
}; 

