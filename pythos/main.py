#we only use standard libraries!!!!!!! hooray!!!!!!!
import ast, math, threading, time
from tkinter import *
from tkinter.ttk import *
from decimal_conversions import *


#todo
#addressing accesses ram right???
#do the gui todo since im sick and tired of dealing with this cli
#rework the cli into an app similar to terminal

#gui todo
#add system for making pixels
#likely to be:
#r12 is color (r*65536)+(g*256)+(b)
#r11 is position (y*screen_width)+(x)

def is_valid_hex(hex):
  #hex must follow official format, all characters uppercase and big endian. 11 is valid (17 in decimal), 0BA765BF is valid (195519935 in decimal), 0ba765bf is not valid (lowercase), FB567AB0 is technically valid but incorrect (big endian is used, not little endian)
  if not isinstance(hex, str):
    return False
  
  hex_characters = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "A", "B", "C", "D", "E", "F"]
  for hex_character in hex:
    if not hex_character in hex_characters:
      return False
  return True

def is_valid_address(address):
  if len(str(address)) > 8:
    return False
  return is_valid_hex(address)

def update_cpsr(result):
  N = "1" if result < 0 else "0"
  Z = "1" if result == 0 else "0"
  C = "1" if len(decimal_to_binary(result)) >= 33 else "0"
  V = "1" if -2147483648 > result <= 2147483648 else "0"
  registers.registers["cpsr"] = f"{N}{Z}{C}{V}"

def instruction_to_binary(instruction):
  binaries = []
  binary = ""
  instruction_name = instruction[0].__name__
  #flag
  if "flag" in instruction_name:
    #flag
    #for some reason .strip("flag") also deletes the "all" in "syscall", so for now instructions cannot contain flag in their name
    instruction_name = instruction_name.replace("flag", "")
    binary += decimal_to_binary(list(flags.flags.keys()).index(instruction[1][0]), 4)
    operand_offset = 1
  #no flag
  else:
    #flag
    binary += "0000"
    operand_offset = 0
  #instruction
  binary += decimal_to_binary(list(instruction_info.keys()).index(instruction_name), 7)
  #operand_1
  operand_1 = instruction_info[instruction_name]["operand_1"]
  if operand_1 != None:
    operand_1 += operand_offset
    operand = instruction[1][operand_1]
    #number
    if isinstance(operand, int):
      binary += "00"
      binary += decimal_to_binary(math.floor((len(decimal_to_binary(operand)) - 1) / 8) + 1, 5)
    #register base
    elif "r" in operand:
      #registers are a bit different, since theyre always 0-15, we can just replace the length with the register number. if its an address, we can just add 32 or whatever.
      binary += "10"
      #register address
      if "0x" in operand:
        binary += "1"
      #register regular
      else:
        binary += "0"
      binary += decimal_to_binary(int(operand.replace("r", "").replace("0x", "")), 4)
    #address
    elif "0x" in operand:
      binary += "01"
      binary += decimal_to_binary(math.floor((len(hex_to_binary(operand)) - 1) / 8) + 1, 5)
    #string
    else:
      binary += "11"
      binary += decimal_to_binary(math.floor(((len(operand) * 8) - 1) / 8) + 1, 5)
  else:
    binary += "0000000"
  #operand_2
  operand_2 = instruction_info[instruction_name]["operand_2"]
  if operand_2 != None:
    operand_2 += operand_offset
    operand = instruction[1][operand_2]
    #number
    if isinstance(operand, int):
      binary += "00"
      binary += decimal_to_binary(math.floor((len(decimal_to_binary(operand)) - 1) / 8) + 1, 5)
    #register base
    elif "r" in operand:
      binary += "10"
      #register address
      if "0x" in operand:
        binary += "1"
      #register regular
      else:
        binary += "0"
      binary += decimal_to_binary(int(operand.replace("r", "").replace("0x", "")), 4)
    #address
    elif "0x" in operand:
      binary += "01"
      binary += decimal_to_binary(math.floor((len(hex_to_binary(operand)) - 1) / 8) + 1, 5)
    #string
    else:
      binary += "11"
      binary += decimal_to_binary(math.floor(((len(operand) * 8) - 1) / 8) + 1, 5)
  else:
    binary += "0000000"
  #operand_3
  operand_3 = instruction_info[instruction_name]["operand_3"]
  if operand_3 != None:
    operand_3 += operand_offset
    operand = instruction[1][operand_3]
    #number
    if isinstance(operand, int):
      binary += "00"
      binary += decimal_to_binary(math.floor((len(decimal_to_binary(operand)) - 1) / 8) + 1, 5)
    #register base
    elif "r" in operand:
      binary += "10"
      #register address
      if "0x" in operand:
        binary += "1"
      #register regular
      else:
        binary += "0"
      binary += decimal_to_binary(int(operand.replace("r", "").replace("0x", "")), 4)
    #address
    elif "0x" in operand:
      binary += "01"
      binary += decimal_to_binary(math.floor((len(hex_to_binary(operand)) - 1) / 8) + 1, 5)
    #string
    else:
      binary += "11"
      binary += decimal_to_binary(math.floor(((len(operand) * 8) - 1) / 8) + 1, 5)
  else:
    binary += "0000000"
  binaries.append(binary)
  
  #operand_1_binary
  if operand_1 != None:
    operand = instruction[1][operand_1]
    #number
    if binary[11:13] == "00":
      operand_1_binary = decimal_to_binary(operand, binary_to_decimal(binary[13:18]) * 8)
    #address
    elif binary[11:13] == "01":
      operand_1_binary = hex_to_binary(operand.replace("0x", ""), binary_to_decimal(binary[13:18]) * 8)
    #register base
    elif binary[11:13] == "10":
      #since the entire register is stored in the header, theres no need to add body data, we just need to capture the register since its a string
      operand_1_binary = ""
    #string
    else:
      operand_1_binary = ascii_string_to_binary(operand, binary_to_decimal(binary[13:18]) * 8, 8)
    binaries.append(operand_1_binary)
  #operand_2_binary
  if operand_2 != None:
    operand = instruction[1][operand_2]
    #number
    if binary[18:20] == "00":
      operand_2_binary = decimal_to_binary(operand, binary_to_decimal(binary[20:25]) * 8)
    #address
    elif binary[18:20] == "01":
      operand_2_binary = hex_to_binary(operand.replace("0x", ""), binary_to_decimal(binary[20:25]) * 8)
    #register base
    elif binary[18:20] == "10":
      #since the entire register is stored in the header, theres no need to add body data, we just need to capture the register since its a string
      operand_2_binary = ""
    #string
    else:
      operand_2_binary = ascii_string_to_binary(operand, binary_to_decimal(binary[20:25]) * 8, 8)
    binaries.append(operand_2_binary)
  #operand_3_binary
  if operand_3 != None:
    operand = instruction[1][operand_3]
    #number
    if binary[25:27] == "00":
      operand_3_binary = decimal_to_binary(operand, binary_to_decimal(binary[27:32]) * 8)
    #address
    elif binary[25:27] == "01":
      operand_3_binary = hex_to_binary(operand.replace("0x", ""), binary_to_decimal(binary[27:32]) * 8)
    #register base
    elif binary[25:27] == "10":
      #since the entire register is stored in the header, theres no need to add body data, we just need to capture the register since its a string
      operand_3_binary = ""
    #string
    else:
      operand_3_binary = ascii_string_to_binary(operand, binary_to_decimal(binary[27:32]) * 8, 8)
    binaries.append(operand_3_binary)
  return binaries

#use this for quick testing
def run_instruction_stack(instruction_stack):
  while True:
    instruction_stack[0][0](*instruction_stack[0][1])
    del instruction_stack[0]
    if len(instruction_stack) == 0:
      break

def psm_to_python(psm):
  instructions = psm.split("\n")
  converted_instructions = []
  #no branches
  if "!no_branches" in instructions:
    for raw_instruction in instructions:
      instruction = raw_instruction.strip()
      if instruction == "":
        continue
      if instruction[0] == ";" or instruction[0] == "!":
        continue
      converted_arguments = []
      for argument in instruction.split(" ")[1:]:
        if ("r" in argument or "0x" in argument) and not '"' in argument:
          converted_arguments.append(argument)
        elif '"' in argument:
          converted_arguments.append(argument.replace('"', ""))
        else:
          converted_arguments.append(int(argument))
      instruction_name = instruction.split(" ")[0]
      if "flag" in instruction_name:
        converted_instructions.append([instruction_info[instruction_name.replace("flag", "")]["flag_function"], converted_arguments])
      else:
        converted_instructions.append([instruction_info[instruction_name]["function"], converted_arguments])
    converted_branches = {}
  #branches
  else:
    for raw_instruction in instructions[:instructions.index("!branches:")]:
      instruction = raw_instruction.strip()
      if instruction == "":
        continue
      if instruction[0] == ";":
        continue
      converted_arguments = []
      for argument in instruction.split(" ")[1:]:
        if ("r" in argument or "0x" in argument) and not '"' in argument:
          converted_arguments.append(argument)
        elif '"' in argument:
          converted_arguments.append(argument.replace('"', ""))
        else:
          converted_arguments.append(int(argument))
      instruction_name = instruction.split(" ")[0]
      if "flag" in instruction_name:
        converted_instructions.append([instruction_info[instruction_name.replace("flag", "")]["flag_function"], converted_arguments])
      else:
        converted_instructions.append([instruction_info[instruction_name]["function"], converted_arguments])
    current_branch = ""
    converted_branches = {}
    used_branches = [0]
    transform_branches = {}
    for raw_instruction in instructions[instructions.index("!branches:") + 1:]:
      instruction = raw_instruction.strip()
      if instruction == "":
        continue
      if instruction[0] == ";":
        continue
      if instruction[0] == ".":
        branch_name = max(used_branches) + 1
        used_branches.append(branch_name)
        transform_branches[instruction[1:]] = branch_name
        converted_branches[branch_name] = []
        current_branch = branch_name
        continue
      converted_arguments = []
      for argument in instruction.split(" ")[1:]:
        if ("r" in argument or "0x" in argument) and not '"' in argument:
          converted_arguments.append(argument)
        elif '"' in argument:
          converted_arguments.append(argument.replace('"', ""))
        else:
          converted_arguments.append(int(argument))
      instruction_name = instruction.split(" ")[0]
      if "flag" in instruction_name:
        converted_branches[current_branch].append([instruction_info[instruction_name.replace("flag", "")]["flag_function"], converted_arguments])
      else:
        converted_branches[current_branch].append([instruction_info[instruction_name]["function"], converted_arguments])
  
    #convert branch instructions to new branch name
    branch_instructions = ["br", "bl"]
    for instruction in converted_instructions:
      instruction_name = instruction[0].__name__
      if instruction_name.replace("flag", "") in branch_instructions:
        if "flag" in instruction_name:
          instruction[1][1] = transform_branches[instruction[1][1]]
        else:
          instruction[1][0] = transform_branches[instruction[1][0]]
    for branch in list(converted_branches.values()):
      for instruction in branch:
        if isinstance(instruction[0], str):
          continue
        instruction_name = instruction[0].__name__
        if instruction_name.replace("flag", "") in branch_instructions:
          if "flag" in instruction_name:
            instruction[1][1] = transform_branches[instruction[1][1]]
          else:
            instruction[1][0] = transform_branches[instruction[1][0]]
  return converted_instructions, converted_branches

def compile_instructions(instruction_stack, tree, address):
  compiled = ""
  binary_instructions = ""
  for instruction in instruction_stack:
    binary_instructions += "".join(instruction_to_binary(instruction))
  compiled += binary_instructions
  if tree == {}:
    #no (period) (branches):
    compiled += ascii_string_to_binary(".n", None, 8)
  else:
    #branches:
    compiled += ascii_string_to_binary("b:", None, 8)
    binary_tree = {}
    for branch_name in tree:
      binary_branch_instructions = ""
      for instruction in tree[branch_name]:
        binary_branch_instructions += "".join(instruction_to_binary(instruction))
      compiled += ascii_string_to_binary(f"{branch_name}:", None, 8)
      compiled += binary_branch_instructions
      #end (period) branch
      compiled += ascii_string_to_binary(".b", None, 8)
  #end (period) assembly
  compiled += ascii_string_to_binary(".a", None, 8)
  start_address = hex_to_decimal(address)
  for decimal_address, binary in enumerate([compiled[i:i + 8] for i in range(0, len(compiled), 8)]):
    ram[decimal_address + start_address] = binary
  #return the length of the compiled instruction in bits in case i need it
  return len(compiled)

def scan_2_bytes(binary, address):
  scanned = binary_to_ascii_string(binary[address: address + 16])
  return scanned

def run_assembly(address, id):
  #instruction flag [0:4]
  #instruction code [4:11]
  #type of op1 [11:13] (00 if number, 01 if address, 10 if register, 11 if string)
  #length of op1 [13:18]
  #type of op2 [18:20] (same as op1)
  #length of op2 [20:25]
  #type of op3 [25:27] (same as op1)
  #length of op3 [27:32]

  joined_ram = "".join(ram)
  registers.registers = {
    "r0": "00000000000000000000000000000000",
    "r1": "00000000000000000000000000000000",
    "r2": "00000000000000000000000000000000",
    "r3": "00000000000000000000000000000000",
    "r4": "00000000000000000000000000000000",
    "r5": "00000000000000000000000000000000",
    "r6": "00000000000000000000000000000000",
    "r7": "00000000000000000000000000000000",
    "r8": "00000000000000000000000000000000",
    "r9": "00000000000000000000000000000000",
    "r10": "00000000000000000000000000000000",
    "r11": "00000000000000000000000000000000",
    "r12": "00000000000000000000000000000000",
    "r13": "00000000000000000000000000000000", #sp, stack pointer, points to the next lowest free address in memory
    "r14": "00000000000000000000000000000000", #lr, link register, on function call this gets updated to a pointer to where the next instruction in the parent function is
    "r15": "00000000000000000000000000000000", #pc, program counter, points to where the next instruction is
    "cpsr": "00000000000000000000000000000000"
  }

  flags.flags = {
    "EQ": "0",
    "NE": "0",
    "GT": "0",
    "LT": "0",
    "GE": "0",
    "LE": "0",
    "CS": "0",
    "CC": "0",
    "MI": "0",
    "PL": "0",
    "AL": "0",
    "NV": "0",
    "VS": "0",
    "VC": "0",
    "HI": "0",
    "LS": "0"
  }

  current_character.current_character = 0
  
  #run through the assembly to find branch addresses
  branch_addresses.branch_addresses = {}
  find_branches_address = hex_to_decimal(address)
  scanned = scan_2_bytes(joined_ram, find_branches_address)
  #THERE IS NO BETTER WAY TO DO THIS BECAUSE THERES NO REPEAT UNTIL LOOPS IN PYTHON FUORHGLUIESHUSHRUEHFDKFK
  while not id in terminate_list:
    #incase something breaks and im sleep deprived THIS IS SUPPOSED TO CHECK 0:16 AND INCREMENT BY 8 INCASE THE PARITY IS ODD
    if scanned == ".n":
      break
    elif scanned == "b:":
      find_branches_address += 16
      scanned = scan_2_bytes(joined_ram, find_branches_address)
      while True:
        branch_name = ""
        while True:
          if binary_to_ascii(joined_ram[find_branches_address: find_branches_address + 8]) == ":":
            find_branches_address += 8
            scanned = scan_2_bytes(joined_ram, find_branches_address)
            break
          else:
            branch_name +=   binary_to_ascii(joined_ram[find_branches_address: find_branches_address + 8])
          find_branches_address += 8
          scanned = scan_2_bytes(joined_ram, find_branches_address)
        branch_addresses.branch_addresses[branch_name] = find_branches_address
        while True:
          if scanned == ".b":
            find_branches_address += 16
            scanned = scan_2_bytes(joined_ram, find_branches_address)
            break
          elif scanned == ".a":
            break
          else:
            find_branches_address += 8
            scanned = scan_2_bytes(joined_ram, find_branches_address)
        if scanned == ".a":
          break
      break
    find_branches_address += 8
    scanned = scan_2_bytes(joined_ram, find_branches_address)
  if id in terminate_list:
    terminate_list.remove(id)
  parent_instruction_addresses.parent_instruction_addresses = []
  current_address.current_address = hex_to_decimal(address)
  registers.registers["r15"] = decimal_to_binary(current_address.current_address, 32)
  while not id in terminate_list:
    flag = binary_to_decimal(joined_ram[current_address.current_address: current_address.current_address + 4])
    instruction_name = list(instruction_info.keys())[binary_to_decimal(joined_ram[current_address.current_address + 4: current_address.current_address + 11])]
    operand_1 = None
    if instruction_info[instruction_name]["operand_1"] != None:
      operand_1_type = joined_ram[current_address.current_address + 11: current_address.current_address + 13]
      if operand_1_type[0] == "0":
        operand_1_type = "number"
      elif operand_1_type == "10":
        operand_1_type = "register"
      elif operand_1_type == "11":
        operand_1_type = "string"
      else:
        operand_1_type = "number"
      operand_1_length = binary_to_decimal("".join(joined_ram[current_address.current_address + 13: current_address.current_address + 18])) * 8
      if operand_1_type == "register":
        operand_1_length = 0
        #to save a small amount of time (and headaches) i can remove the operand_<num>_length and keep the previous ones
        if joined_ram[current_address.current_address + 13: current_address.current_address + 14] == "0":
          operand_1 = f"r{binary_to_decimal(''.join(joined_ram[current_address.current_address + 14: current_address.current_address + 18]))}"
        else:
          operand_1 = f"0xr{binary_to_decimal(''.join(joined_ram[current_address.current_address + 14: current_address.current_address + 18]))}"
      elif operand_1_type == "number":
        operand_1 = binary_to_decimal("".join(joined_ram[current_address.current_address + 32: current_address.current_address + 32 + operand_1_length]))
      elif operand_1_type == "string":
        operand_1 = binary_to_ascii_string("".join(joined_ram[current_address.current_address + 32: current_address.current_address + 32 + operand_1_length]))
    else:
      operand_1_length = 0
    operand_2 = None
    if instruction_info[instruction_name]["operand_2"] != None:
      operand_2_type = joined_ram[current_address.current_address + 18: current_address.current_address + 20]
      if operand_2_type[0] == "0":
        operand_2_type = "number"
      elif operand_2_type == "10":
        operand_2_type = "register"
      elif operand_2_type == "11":
        operand_2_type = "string"
      else:
        operand_2_type = "number"
      operand_2_length = binary_to_decimal("".join(joined_ram[current_address.current_address + 20: current_address.current_address + 25])) * 8
      if operand_2_type == "register":
        operand_2_length = 0
        if joined_ram[current_address.current_address + 20 + operand_1_length: current_address.current_address + 21 + operand_1_length] == "0":
          operand_2 = f"r{binary_to_decimal(''.join(joined_ram[current_address.current_address + 21 + operand_1_length: current_address.current_address + 25 + operand_1_length]))}"
        else:
          operand_2 = f"0xr{binary_to_decimal(''.join(joined_ram[current_address.current_address + 21 + operand_1_length: current_address.current_address + 25 + operand_1_length]))}"
      elif operand_2_type == "number":
        operand_2 = binary_to_decimal("".join(joined_ram[current_address.current_address + 32 + operand_1_length: current_address.current_address + 32 + operand_1_length + operand_2_length]))
      elif operand_2_type == "string":
        operand_2 = binary_to_ascii_string("".join(joined_ram[current_address.current_address + 32 + operand_1_length: current_address.current_address + 32 + operand_1_length + operand_2_length]))
    else:
      operand_2_length = 0
    operand_3 = None
    if instruction_info[instruction_name]["operand_3"] != None:
      operand_3_type = joined_ram[current_address.current_address + 25: current_address.current_address + 27]
      if operand_3_type[0] == "0":
        operand_3_type = "number"
      elif operand_3_type == "10":
        operand_3_type = "register"
      elif operand_3_type == "11":
        operand_3_type = "string"
      else:
        operand_3_type = "number"
      operand_3_length = binary_to_decimal("".join(joined_ram[current_address.current_address + 27: current_address.current_address + 32])) * 8
      if operand_3_type == "register":
        operand_3_length = 0
        if joined_ram[current_address.current_address + 27 + operand_1_length + operand_2_length: current_address.current_address + 28 + operand_1_length + operand_2_length] == "0":
          operand_3 = f"r{binary_to_decimal(''.join(joined_ram[current_address.current_address + 28 + operand_1_length + operand_2_length: current_address.current_address + 32 + operand_1_length + operand_2_length]))}"
        else:
          operand_3 = f"0xr{binary_to_decimal(''.join(joined_ram[current_address.current_address + 28 + operand_1_length + operand_2_length: current_address.current_address + 32 + operand_1_length + operand_2_length]))}"
      elif operand_3_type == "number":
        operand_3 = binary_to_decimal("".join(joined_ram[current_address.current_address + 32 + operand_1_length + operand_2_length: current_address.current_address + 32 + operand_1_length + operand_2_length + operand_3_length]))
      elif operand_3_type == "string":
        operand_3 = binary_to_ascii_string("".join(joined_ram[current_address.current_address + 32 + operand_1_length + operand_2_length: current_address.current_address + 32 + operand_1_length + operand_2_length + operand_3_length]))
    else:
      operand_3_length = 0
    registers.registers["r15"] = decimal_to_binary(binary_to_decimal(registers.registers["r15"]) + 32 + operand_1_length + operand_2_length + operand_3_length, 32)
    if flag > 0:
      if flags.flags[list(flags.flags.keys())[flag]] == "0":
        current_address.current_address = binary_to_decimal(registers.registers["r15"])
        continue
    if instruction_name in branch_addresses.branch_addresses:
      registers.registers["r15"] = decimal_to_binary(branch_addresses.branch_addresses[branch], 32)
    instruction_info[instruction_name]["function"](*[i for i in [operand_1, operand_2, operand_3] if i != None])
    if instruction_name == "syscall" and operand_1 == 0:
      break
    current_address.current_address = binary_to_decimal(registers.registers["r15"])
  if id in terminate_list:
    terminate_list.remove(id)

def event_handler():
  global text, terminate, terminate_list, ids, storage

  #just in case a function needs it
  registers.registers = {
    "r0": "00000000000000000000000000000000",
    "r1": "00000000000000000000000000000000",
    "r2": "00000000000000000000000000000000",
    "r3": "00000000000000000000000000000000",
    "r4": "00000000000000000000000000000000",
    "r5": "00000000000000000000000000000000",
    "r6": "00000000000000000000000000000000",
    "r7": "00000000000000000000000000000000",
    "r8": "00000000000000000000000000000000",
    "r9": "00000000000000000000000000000000",
    "r10": "00000000000000000000000000000000",
    "r11": "00000000000000000000000000000000",
    "r12": "00000000000000000000000000000000",
    "r13": "00000000000000000000000000000000",
    "r14": "00000000000000000000000000000000",
    "r15": "00000000000000000000000000000000",
    "cpsr": "00000000000000000000000000000000"
  }

  flags.flags = {
    "EQ": "0",
    "NE": "0",
    "GT": "0",
    "LT": "0",
    "GE": "0",
    "LE": "0",
    "CS": "0",
    "CC": "0",
    "MI": "0",
    "PL": "0",
    "AL": "0",
    "NV": "0",
    "VS": "0",
    "VC": "0",
    "HI": "0",
    "LS": "0"
  }
  
  #wait for text to not be empty
  while True:
    try:
      if text["text"] != "":
        break
    except:
      pass
  old_split_length = 0
      
  while True:
    while True:
      try:
        if text["text"].split("\r")[-1] != "":
          break
      except:
        pass
    while True:
      try:
        if text["text"].split("\r")[-1] == "":
          break
      except:
        pass
    returns = len(text["text"].split("\r"))
    if returns == 1 or returns <= old_split_length:
      continue
    old_split_length = returns
    command = text["text"].split("\r")[-2]
    tokens = command.split(" ")
    if tokens[0] == "help":
      text["text"] += """help: Returns a list of all default commands and their functions.

run <address>: Runs the assembly at address <address>.

write <address> <code>: Writes assembly at address <address>, a newline must be added (using shift + enter) after the address before adding code.

clear: Clears the text in the CLI.

import file <data_type> <file_path> <address>: Imports an external file with type <data_type> ("raw" or "binary") at location <file_path> to address <address>.

import storage <storage_address> <address>: Imports from storage at address <store_address> to address <address>.\r"""
    elif tokens[0] == "run":
      if len(ids) == 0:
        id = 0
      else:
        id = len(ids)
      ids.append(id)
      assembly_thread = threading.Thread(target=run_assembly, args=[tokens[1], id])
      assembly_thread.start()
      while True:
        if assembly_thread.is_alive():
          if terminate:
            terminate_list.append(id)
            terminate = False
            break
        else:
          break
      assembly_thread.join()
      ids.remove(id)
    elif tokens[0] == "write":
      converted_instructions, converted_branches = psm_to_python("\n".join(command.split("\n")[1:]))
      compile_instructions(converted_instructions, converted_branches, tokens[1])
    elif tokens[0] == "clear":
      text["text"] = ""
      old_split_length = 0
    elif tokens[0] == "import":
      if tokens[1] == "file":
        if tokens[2] == "binary":
          binary_file = open(tokens[3], "r")
          data = ast.literal_eval(binary_file.read())
          binary_file.close()
          for increment, value in enumerate(data):
            ram[hex_to_decimal(tokens[4]) + increment] = value
        elif tokens[2] == "raw":
          raw_file = open(tokens[3], "r")
          psm_data = raw_file.read()
          raw_file.close()
          converted_instructions, converted_branches = psm_to_python(psm_data)
          compile_instructions(converted_instructions, converted_branches, tokens[4])
      elif tokens[1] == "storage":
        joined_storage = "".join(storage)
        data = ""
        increment = hex_to_decimal(tokens[2])
        while True:
          data += storage[math.floor(increment / 8)]
          increment += 8
          scanned = scan_2_bytes(joined_storage, increment)
          if scanned == ".a":
            data += "a"
            for increment, value in enumerate(data):
              ram[hex_to_decimal(tokens[3]) + increment] = value

def tkinter_handler():
  global text
  #wait for tkinter to initialize
  while True:
    try:
      if text:
        break
    except:
      pass

  screen_height = main_window.winfo_screenheight()
  while True:
    #ok if you get unlucky the length of the text can change after checking its length so rather than have to deal with that im going to use the much simpler solution
    try:
      last_character = text["text"][-1]
    except:
      continue
    if last_character == "\r":
      text.place_configure(y=screen_height - text.winfo_height() - 37)
    else:
      text.place_configure(y=screen_height - text.winfo_height() - 21)

def storage_handler():
  #tbh i just think that constantly writing to storage is better than having to manually write constantly, and should improve performance
  global storage, write_storage
  #.psb = PythoSBinary
  storage_file = open("../storage.psb", "w")
  time_since_write = 0
  while True:
    #if we havent written for 10 seconds, write in order to prevent memory loss
    if time_since_write >= 10 or write_storage:
      #for a minor size increase (~37.5%) we can decrease the time this takes to load from 30+ seconds to <2 by choosing to keep the list intact rather than converting it to raw binary and writing that
      storage_file.write(str(storage))
      time_since_write = 0
      write_storage = False
    else:
      time_since_write += 1
    time.sleep(1)

def prepare_os():
  global configuration, instruction_info, data, ram, storage, text_input, terminate, terminate_list, ids, global_current_character, write_storage
  #thread specific globals
  global registers, flags, parent_instruction_addresses, current_address, branch_addresses, current_character
  #None = unused
  #Number (0, 1, 2...) = index of arguments where this is found
  instruction_info = {
    "mov": {
      "operand_1": 0,
      "operand_2": 1,
      "operand_3": None,
      "function": mov,
      "flag_function": movflag
    },
    "ldrr": {
      "operand_1": 0,
      "operand_2": 1,
      "operand_3": None,
      "function": ldrr,
      "flag_function": ldrrflag
    },
    "ldrs": {
      "operand_1": 0,
      "operand_2": 1,
      "operand_3": None,
      "function": ldrs,
      "flag_function": ldrsflag
    },
    #debating on keeping these
    #"strr": {
    #  "operand_1": 0,
    #  "operand_2": 1,
    #  "operand_3": None,
    #  "function": strr,
    #  "flag_function": strrflag
    #},
    #"strs": {
    #  "operand_1": 0,
    #  "operand_2": 1,
    #  "operand_3": None,
    #  "function": strs,
    #  "flag_function": strsflag
    #},
    "add": {
      "operand_1": 0,
      "operand_2": 1,
      "operand_3": 2,
      "function": add,
      "flag_function": addflag
    },
    "sub": {
      "operand_1": 0,
      "operand_2": 1,
      "operand_3": 2,
      "function": sub,
      "flag_function": subflag
    },
    "mul": {
      "operand_1": 0,
      "operand_2": 1,
      "operand_3": 2,
      "function": mul,
      "flag_function": mulflag
    },
    "cmp": {
      "operand_1": 0,
      "operand_2": 1,
      "operand_3": None,
      "function": cmp,
      "flag_function": cmpflag
    },
    "br": {
      "operand_1": 0,
      "operand_2": None,
      "operand_3": None,
      "function": br,
      "flag_function": brflag
    },
    "bl": {
      "operand_1": 0,
      "operand_2": None,
      "operand_3": None,
      "function": bl,
      "flag_function": blflag
    },
    "push": {
      "operand_1": 0,
      "operand_2": None,
      "operand_3": None,
      "function": push,
      "flag_function": pushflag
    },
    "pop": {
      "operand_1": 0,
      "operand_2": None,
      "operand_3": None,
      "function": pop,
      "flag_function": popflag
    },
    "syscall": {
      "operand_1": 0,
      "operand_2": None,
      "operand_3": None,
      "function": syscall,
      "flag_function": syscallflag
    }
  }

  try:
    configuration_file = open("../pythos.cfg", "r")
  except:
    create_configuration_file = open("../pythos.cfg", "x")
    create_configuration_file.close()
    configuration_file = open("../pythos.cfg", "w")
    #1 mib default
    configuration = {
      "version": "-1.1.0",
      "storage_size": 1048576,
      "ram_size": 1048576
    }
    configuration_file.write(str(configuration))
    configuration_file.close()
  else:
    configuration = ast.literal_eval(configuration_file.read())

  registers = threading.local()
  flags = threading.local()
  parent_instruction_addresses = threading.local()
  current_address = threading.local()
  branch_addresses = threading.local()
  current_character = threading.local()

  ram = []
  for increment in range(configuration["ram_size"]):
    ram.append("00000000")

  storage = []
  for increment in range(configuration["storage_size"]):
    storage.append("00000000")
  try:
    true_storage = open("../storage.psb", "r")
  except:
    create_storage_file = open("../storage.psb", "x")
    create_storage_file.close()
    true_storage = open("../storage.psb", "r")
  read = true_storage.read()
  if read == "":
    write_storage = True
  if input("Empty storage? (Y/n)\n").lower() == "y":
    write_storage = True
  else:
    try:
      storage = ast.literal_eval(str(read))
    except:
      if input("Couldn't read storage.psb, check to make sure it's valid. If you want to reset storage.psb please input Y or y.\n").lower() == "y":
        write_storage()
      try:
        true_storage.seek(0)
        storage = ast.literal_eval(true_storage.read())
      except:
        true_storage.close()
        raise Exception("Failed to read storage from storage.psb for a second time. Please either delete storage.psb and rerun the program, or ensure no corruption of storage.psb has occurred then rerun the program.")
  true_storage.close()
  text_input = None
  global_current_character = 0
  terminate = False
  terminate_list = []
  ids = []
  event_thread = threading.Thread(target=event_handler, daemon=True)
  event_thread.start()
  tkinter_thread = threading.Thread(target=tkinter_handler, daemon=True)
  tkinter_thread.start()
  write_storage_thread = threading.Thread(target=storage_handler, daemon=True)
  write_storage_thread.start()



def update_text_with_key(key):
  global text_input, terminate, global_current_character
  text_input = key.char
  global_current_character += 1
  if key.char in special_keys:
    if key.char == "\x08":
      text["text"] = text["text"][:-1]
    elif key.char == "\r":
      if key.state == 1:
        text["text"] = f"{text['text']}\n"
      else:
        text["text"] = f"{text['text']}\r"
    elif key.char == "\x03":
      terminate = True
  else:
    text["text"] = text["text"] + key.char



def mov(store_label, info):
  if isinstance(info, int):
    registers.registers[store_label] = decimal_to_binary(info, 32)
  elif "r" in info:
    if "0x" in info:
      registers.registers[store_label] = ram[binary_to_decimal(registers.registers[info.replace("0x", "")])]
    else:
      registers.registers[store_label] = registers.registers[info]
  elif "0x" in info:
    registers.registers[store_label] = ram[hex_to_decimal(info.replace("0x", ""))]

def movflag(flag, register, info):
  if flags.flags[flag] == "1":
    mov(register, info)


#load ram
def ldrr(register, label):
  if "r" in label:
    registers.registers[register] = decimal_to_binary(binary_to_decimal(ram[binary_to_decimal(registers.registers[label.replace("0x", "")])]), 32)
  else:
    registers.registers[register] = decimal_to_binary(binary_to_decimal(ram[hex_to_decimal(label.replace("0x", ""))]), 32)

def ldrrflag(flag, register, label):
  if flags.flags[flag] == "1":
    ldrr(register, label)


#load storage
def ldrs(register, label):
  if "r" in label:
    registers.registers[register] = decimal_to_binary(binary_to_decimal(storage[hex_to_decimal(registers.registers[label.replace("0x", "")])]), 32)
  else:
    registers.registers[register] = decimal_to_binary(binary_to_decimal(storage[hex_to_decimal(label.replace("0x", ""))]), 32)

def ldrsflag(flag, register, label):
  if flags.flags[flag] == "1":
    ldrs(register, label)


#store ram
def strr(label, store_label):
  register_size = math.ceil(len(registers.registers[label]) / 8)
  if "r" in store_label:
    for increment in range(register_size):
      ram[(binary_to_decimal(registers.registers[store_label.replace("0x", "")]) * 4) + increment] = registers.registers[label][increment * 8: (increment * 8) + 8]
  else:
    for increment in range(register_size):
      ram[(hex_to_decimal(store_label.replace("0x", "")) * 4) + increment] = registers.registers[label][increment * 8: (increment * 8) + 8]

def strrflag(flag, label, store_label):
  if flags.flags[flag] == "1":
    strr(label, store_label)


#store storage
def strs(register, store_label):
  register_size = math.ceil(len(registers.registers[register]) / 8)
  if "r" in store_label:
    for increment in range(register_size):
      storage[(binary_to_decimal(registers.registers[store_label.replace("0x", "")]) * 4) + increment] = registers.registers[register][increment * 8: (increment * 8) + 8]
  else:
    for increment in range(register_size):
      storage[(hex_to_decimal(store_label.replace("0x", "")) * 4) + increment] = registers.registers[register][increment * 8: (increment * 8) + 8]

def strsflag(flag, register, store_label):
  if flags.flags[flag] == "1":
    strs(register, store_label)


def add(store_register, operand_1, operand_2):
  if isinstance(operand_2, int):
    if isinstance(operand_1, int):
      sum = operand_1 + operand_2
    elif "r" in operand_1:
      if "0x" in operand_1:
        sum = binary_to_decimal(ram[binary_to_decimal(registers.registers[operand_1])]) + operand_2
      else:
        sum = binary_to_decimal(registers.registers[operand_1]) + operand_2
    elif "0x" in operand_1:
      sum = binary_to_decimal(ram[hex_to_decimal(operand_1.replace("0x", ""))]) + operand_2
  elif "r" in operand_2:
    if "0x" in operand_2:
      if isinstance(operand_1, int):
        sum = operand_1 + binary_to_decimal(ram[binary_to_decimal(registers.registers[operand_2.replace("0x", "")])])
      elif "r" in operand_1:
        if "0x" in operand_1:
          sum = binary_to_decimal(ram[binary_to_decimal(registers.registers[operand_1])]) + binary_to_decimal(ram[binary_to_decimal(registers.registers[operand_2.replace("0x", "")])])
        else:
          sum = binary_to_decimal(registers.registers[operand_1]) + binary_to_decimal(ram[binary_to_decimal(registers.registers[operand_2.replace("0x", "")])])
      elif "0x" in operand_1:
        sum = binary_to_decimal(ram[hex_to_decimal(operand_1.replace("0x", ""))]) + binary_to_decimal(ram[binary_to_decimal(registers.registers[operand_2.replace("0x", "")])])
    else:
      if isinstance(operand_1, int):
        sum = operand_1 + binary_to_decimal(registers.registers[operand_2])
      elif "r" in operand_1:
        if "0x" in operand_1:
          sum = binary_to_decimal(ram[binary_to_decimal(registers.registers[operand_1])]) + binary_to_decimal(registers.registers[operand_2])
        else:
          sum = binary_to_decimal(registers.registers[operand_1]) + binary_to_decimal(registers.registers[operand_2])
      elif "0x" in operand_1:
        sum = binary_to_decimal(ram[hex_to_decimal(operand_1.replace("0x", ""))]) + binary_to_decimal(registers.registers[operand_2])
  elif "0x" in operand_2:
    if isinstance(operand_1, int):
      sum = operand_1 + binary_to_decimal(ram[hex_to_decimal(operand_2.replace("0x", ""))])
    elif "r" in operand_1:
      if "0x" in operand_1:
        sum = binary_to_decimal(ram[binary_to_decimal(registers.registers[operand_1])]) + binary_to_decimal(ram[hex_to_decimal(operand_2.replace("0x", ""))])
      else:
        sum = binary_to_decimal(registers.registers[operand_1]) + binary_to_decimal(ram[hex_to_decimal(operand_2.replace("0x", ""))])
    elif "0x" in operand_1:
      sum = binary_to_decimal(ram[hex_to_decimal(operand_1.replace("0x", ""))]) + binary_to_decimal(ram[hex_to_decimal(operand_2.replace("0x", ""))])
  update_cpsr(sum)
  if store_register != None:
    registers.registers[store_register] = decimal_to_binary(sum, 32)

def addflag(flag, store_register, register, info):
  if flags.flags[flag] == "1":
    add(store_register, register, info)


def sub(store_register, operand_1, operand_2, cmp=False):
  if isinstance(operand_2, int):
    if isinstance(operand_1, int):
      difference = operand_1 - operand_2
    elif "r" in operand_1:
      if "0x" in operand_1:
        difference = binary_to_decimal(ram[binary_to_decimal(registers.registers[operand_1])]) - operand_2
      else:
        difference = binary_to_decimal(registers.registers[operand_1]) - operand_2
    elif "0x" in operand_1:
      difference = binary_to_decimal(ram[hex_to_decimal(operand_1.replace("0x", ""))]) - operand_2
  elif "r" in operand_2:
    if "0x" in operand_2:
      if isinstance(operand_1, int):
        difference = operand_1 - binary_to_decimal(ram[binary_to_decimal(registers.registers[operand_2.replace("0x", "")])])
      elif "r" in operand_1:
        if "0x" in operand_1:
          difference = binary_to_decimal(ram[binary_to_decimal(registers.registers[operand_1])]) - binary_to_decimal(ram[binary_to_decimal(registers.registers[operand_2.replace("0x", "")])])
        else:
          difference = binary_to_decimal(registers.registers[operand_1]) - binary_to_decimal(ram[binary_to_decimal(registers.registers[operand_2.replace("0x", "")])])
      elif "0x" in operand_1:
        difference = binary_to_decimal(ram[hex_to_decimal(operand_1.replace("0x", ""))]) - binary_to_decimal(ram[binary_to_decimal(registers.registers[operand_2.replace("0x", "")])])
    else:
      if isinstance(operand_1, int):
        difference = operand_1 - binary_to_decimal(registers.registers[operand_2])
      elif "r" in operand_1:
        if "0x" in operand_1:
          difference = binary_to_decimal(ram[binary_to_decimal(registers.registers[operand_1])]) - binary_to_decimal(registers.registers[operand_2])
        else:
          difference = binary_to_decimal(registers.registers[operand_1]) - binary_to_decimal(registers.registers[operand_2])
      elif "0x" in operand_1:
        difference = binary_to_decimal(ram[hex_to_decimal(operand_1.replace("0x", ""))]) - binary_to_decimal(registers.registers[operand_2])
  elif "0x" in operand_2:
    if isinstance(operand_1, int):
      difference = operand_1 - binary_to_decimal(ram[hex_to_decimal(operand_2.replace("0x", ""))])
    elif "r" in operand_1:
      if "0x" in operand_1:
        difference = binary_to_decimal(ram[binary_to_decimal(registers.registers[operand_1])]) - binary_to_decimal(ram[hex_to_decimal(operand_2.replace("0x", ""))])
      else:
        difference = binary_to_decimal(registers.registers[operand_1]) - binary_to_decimal(ram[hex_to_decimal(operand_2.replace("0x", ""))])
    elif "0x" in operand_1:
      difference = binary_to_decimal(ram[hex_to_decimal(operand_1.replace("0x", ""))]) - binary_to_decimal(ram[hex_to_decimal(operand_2.replace("0x", ""))])
  update_cpsr(difference)
  if store_register != None:
    registers.registers[store_register] = decimal_to_binary(difference, 32)

def subflag(flag, store_register, register, info):
  if flags.flags[flag] == "1":
    sub(store_register, register, info)


def mul(store_register, operand_1, operand_2):
  if isinstance(operand_2, int):
    if isinstance(operand_1, int):
      multiplied = operand_1 * operand_2
    elif "r" in operand_1:
      if "0x" in operand_1:
        multiplied = binary_to_decimal(ram[binary_to_decimal(registers.registers[operand_1])]) * operand_2
      else:
        multiplied = binary_to_decimal(registers.registers[operand_1]) * operand_2
    elif "0x" in operand_1:
      multiplied = binary_to_decimal(ram[hex_to_decimal(operand_1.replace("0x", ""))]) * operand_2
    update_cpsr(multiplied)
  elif "r" in operand_2:
    if isinstance(operand_1, int):
      multiplied = operand_1 * binary_to_decimal(ram[binary_to_decimal(registers.registers[operand_2.replace("0x", "")])])
    elif "r" in operand_1:
      if "0x" in operand_1:
        multiplied = binary_to_decimal(ram[binary_to_decimal(registers.registers[operand_1])]) * binary_to_decimal(ram[binary_to_decimal(registers.registers[operand_2.replace("0x", "")])])
      else:
        multiplied = binary_to_decimal(registers.registers[operand_1]) * binary_to_decimal(ram[binary_to_decimal(registers.registers[operand_2.replace("0x", "")])])
    elif "0x" in operand_1:
      multiplied = binary_to_decimal(ram[hex_to_decimal(operand_1.replace("0x", ""))]) * binary_to_decimal(ram[binary_to_decimal(registers.registers[operand_2.replace("0x", "")])])
    update_cpsr(multiplied)
  elif "0x" in operand_2:
    if isinstance(operand_1, int):
      multiplied = operand_1 * binary_to_decimal(ram[hex_to_decimal(operand_2.replace("0x", ""))])
    elif "r" in operand_1:
      if "0x" in operand_1:
        multiplied = binary_to_decimal(ram[binary_to_decimal(registers.registers[operand_1])]) * binary_to_decimal(ram[hex_to_decimal(operand_2.replace("0x", ""))])
      else:
        multiplied = binary_to_decimal(registers.registers[operand_1]) * binary_to_decimal(ram[hex_to_decimal(operand_2.replace("0x", ""))])
    elif "0x" in operand_1:
      multiplied = binary_to_decimal(ram[hex_to_decimal(operand_1.replace("0x", ""))]) * binary_to_decimal(ram[hex_to_decimal(operand_2.replace("0x", ""))])
    update_cpsr(multiplied)
  if store_register != None:
    registers.registers[store_register] = decimal_to_binary(multiplied, 32)

def mulflag(flag, store_register, register, info):
  if flags.flags[flag] == "1":
    mul(store_register, register, info)


def cmp(register, info):
  sub(None, register, info, True)
  flag_set = False
  if registers.registers["cpsr"][1] == "1":
    flag_set = True
    flags.flags["EQ"] = "1"
  else:
    flags.flags["EQ"] = "0"
  if registers.registers["cpsr"][1] == "0":
    flag_set = True
    flags.flags["NE"] = "1"
  else:
    flags.flags["NE"] = "0"
  if registers.registers["cpsr"][1] == "0" and registers.registers["cpsr"][0] == registers.registers["cpsr"][3]:
    flag_set = True
    flags.flags["GT"] = "1"
  else:
    flags.flags["GT"] = "0"
  if registers.registers["cpsr"][0] != registers.registers["cpsr"][3]:
    flag_set = True
    flags.flags["LT"] = "1"
  else:
    flags.flags["LT"] = "0"
  if registers.registers["cpsr"][0] == registers.registers["cpsr"][3]:
    flag_set = True
    flags.flags["GE"] = "1"
  else:
    flags.flags["GE"] = "0"
  if registers.registers["cpsr"][1] == "1" or registers.registers["cpsr"][0] != registers.registers["cpsr"][3]:
    flag_set = True
    flags.flags["LE"] = "1"
  else:
    flags.flags["LE"] = "0"
  if registers.registers["cpsr"][2] == "1":
    flag_set = True
    flags.flags["CS"] = "1"
  else:
    flags.flags["CS"] = "0"
  if registers.registers["cpsr"][2] == "0":
    flag_set = True
    flags.flags["CC"] = "1"
  else:
    flags.flags["CC"] = "0"
  if registers.registers["cpsr"][0] == "1":
    flag_set = True
    flags.flags["MI"] = "1"
  else:
    flags.flags["MI"] = "0"
  if registers.registers["cpsr"][0] == "0":
    flag_set = True
    flags.flags["PL"] = "1"
  else:
    flags.flags["PL"] = "0"
  #what is this flag
  flags.flags["NV"] = "0"
  if registers.registers["cpsr"][3] == "1":
    flag_set = True
    flags.flags["VS"] = "1"
  else:
    flags.flags["VS"] = "0"
  if registers.registers["cpsr"][3] == "0":
    flag_set = True
    flags.flags["VC"] = "1"
  else:
    flags.flags["VC"] = "0"
  if registers.registers["cpsr"][2] == "1" and registers.registers["cpsr"][1] == "0":
    flag_set = True
    flags.flags["HI"] = "1"
  else:
    flags.flags["HI"] = "0"
  if registers.registers["cpsr"][2] == "0" or registers.registers["cpsr"][1] == "0":
    flag_set = True
    flags.flags["LS"] = "1"
  else:
    flags.flags["LS"] = "0"
  if not flag_set:
    flags.flags["AL"] = "1"
  else:
    flags.flags["AL"] = "0"

def cmpflag(flag, register, info):
  if flags.flags[flag] == "1":
    cmp(register, info)


def br(int_branch):
  branch = str(int_branch)
  registers.registers["r15"] = decimal_to_binary(branch_addresses.branch_addresses[branch], 32)

def brflag(flag, int_branch):
  if flags.flags[flag] == "1":
    br(int_branch)


def bl(int_branch):
  branch = str(int_branch)
  #for convenience purposes since removing this would possibly break a couple of programs when trying to go up multiple parents
  parent_instruction_addresses.parent_instruction_addresses.insert(0, decimal_to_binary(current_address.current_address + 32 + len(ascii_string_to_binary(branch, None, 8)), 32))
  registers.registers["r14"] = current_address.current_address + 32 + len(ascii_string_to_binary(branch, None, 8))
  registers.registers["r15"] = decimal_to_binary(branch_addresses.branch_addresses[branch], 32)

def blflag(flag, int_branch):
  if flags.flags[flag] == "1":
    bl(int_branch)


def jmp(address):
  registers.registers["r15"] = decimal_to_binary(address, 32)

def jmpflag(flag, address):
  if flags.flags[flag] == "1":
    jmp(address)


def push(label):
  registers.registers["r13"] = decimal_to_binary(binary_to_decimal(registers.registers["r13"]) - 4, 32)
  #because of how python's indexing works (starts at 0), these must be shifted back one to offset for the sp being 128 rather than 127
  if isinstance(label, int):
    ram[binary_to_decimal(registers.registers["r13"]) - 4: binary_to_decimal(registers.registers["r13"]) - 1] = [decimal_to_binary(label, 32)[i:i + 8] for i in range(0, 32, 8)]
  elif "r" in label:
    if "0x" in label:
      ram[binary_to_decimal(registers.registers["r13"]) - 4: binary_to_decimal(registers.registers["r13"]) - 1] = [ram[binary_to_decimal(registers.registers[label.replace("0x", "")])][i:i + 8] for i in range(0, 32, 8)]
    else:
      ram[binary_to_decimal(registers.registers["r13"]) - 4: binary_to_decimal(registers.registers["r13"]) - 1] = [registers.registers[label][i:i + 8] for i in range(0, 32, 8)]
  elif "0x" in label:
    ram[binary_to_decimal(registers.registers["r13"]) - 4: binary_to_decimal(registers.registers["r13"]) - 1] = [ram[hex_to_decimal(label.replace("0x", ""))][i:i + 8] for i in range(0, 32, 8)]

def pushflag(flag, register):
  if flags.flags[flag] == "1":
    push(register)


def pop(register):
  registers.registers[register] = "".join(ram[binary_to_decimal(registers.registers["r13"]) - 4: binary_to_decimal(registers.registers["r13"])])
  ram[binary_to_decimal(registers.registers["r13"]) - 4: binary_to_decimal(registers.registers["r13"])] = ["00000000", "00000000", "00000000", "00000000"]
  registers.registers["r13"] = decimal_to_binary(binary_to_decimal(registers.registers["r13"]) + 4, 32)

def popflag(flag, register):
  if flags.flags[flag] == "1":
    pop(register)


def syscall(call):
  #syscall 0 is an exit
  #print ascii representation of r12
  if call == 1:
    global text
    text["text"] += binary_to_ascii(registers.registers["r12"])
  #check for input and put it into r12
  if call == 2:
    global text_input, global_current_character
    if global_current_character != current_character.current_character:
      registers.registers["r12"] = ascii_to_binary(text_input, 32)
      current_character.current_character = global_current_character
    else:
      registers.registers["r12"] = "00000000000000000000000000000000"
  #return to parent branch
  elif call == 3:
    registers.registers["r15"] = parent_instruction_addresses.parent_instruction_addresses.pop(0)
  #write storage
  elif call == 4:
    global write_storage
    write_storage = True

def syscallflag(flag, call):
  if flags.flags[flag] == "1":
    syscall(call)



prepare_os()

special_keys = ["\r", "\x08", "\x03"]
main_window = Tk()

main_window["background"] = "black"
main_window.geometry(f"{main_window.winfo_screenwidth()}x{main_window.winfo_screenheight()}")
text = Label(main_window, text="", foreground="white", background="black", wraplength=main_window.winfo_screenwidth(), justify=LEFT)
text.place(x=0, y=0, anchor=NW)
main_window.bind("<KeyPress>", update_text_with_key)
mainloop()
