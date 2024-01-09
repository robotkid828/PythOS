#we only use standard libraries!!!!!!! hooray!!!!!!!
import ast, math, threading
from tkinter import *
from tkinter.ttk import *
from decimal_conversions import *


#todo
#screw it im pushing to github
#i used so many global things please remove all of them thanks

#gui todo (unlikely to happen for a while)
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

def update_cpsr(register, result):
  N = "1" if result < 0 else "0"
  Z = "1" if result == 0 else "0"
  C = "1" if len(decimal_to_binary(result)) >= 33 else "0"
  V = "1" if -2147483648 > result <= 2147483648 else "0"
  registers.registers["cpsr"] = f"{N}{Z}{C}{V}"

def write_storage():
  global storage
  #.psb = PythoSBinary
  true_storage = open("storage.psb", "w")
  #for a minor size increase (~37.5%) we can decrease the time this takes to load from 30+ seconds to <2 by choosing to keep the list intact rather than converting it to raw binary and writing that
  true_storage.write(str(storage))
  true_storage.close()

def instruction_to_binary(instruction):
  binaries = []
  binary = ""
  instruction_name = instruction[0].__name__
  #flag
  if "flag" in instruction_name:
    #flag
    #for some reason .strip("flag") also deletes the "all" in "syscall", so for now instructions cannot contain flag in their name
    instruction_name = instruction_name.replace("flag", "")
    binary += decimal_to_binary(list(flags.keys()).index(instruction[1][0]) + 1, 4)
    #instruction
    binary += decimal_to_binary(list(instruction_info.keys()).index(instruction_name), 7)
    #operand_1
    operand_1 = instruction_info[instruction_name]["operand_1"]
    if operand_1 != None:
      operand_1 += 1
      operand = instruction[1][operand_1]
      #register
      if operand in registers.registers:
        binary += "10"
        binary += decimal_to_binary(math.floor((len(decimal_to_binary(int(operand.replace("r", "")))) - 1) / 8) + 1, 5)
      #address
      elif is_valid_address(operand):
        binary += "0"
        binary += decimal_to_binary(math.floor((len(hex_to_binary(operand)) - 1) / 8) + 1, 6)
      #number
      elif isinstance(operand, int):
        binary += "0"
        binary += decimal_to_binary(math.floor((len(decimal_to_binary(operand)) - 1) / 8) + 1, 6)
      #string
      else:
        binary += "11"
        binary += decimal_to_binary(math.floor(((len(operand) * 8) - 1) / 8) + 1, 5)
    else:
      binary += "0000000"
    #operand_2
    operand_2 = instruction_info[instruction_name]["operand_2"]
    if operand_2 != None:
      operand_2 += 1
      operand = instruction[1][operand_2]
      #register
      if operand in registers.registers:
        binary += "10"
        binary += decimal_to_binary(math.floor((len(decimal_to_binary(int(operand.replace("r", "")))) - 1) / 8) + 1, 5)
      #address
      elif is_valid_address(operand):
        binary += "0"
        binary += decimal_to_binary(math.floor((len(hex_to_binary(operand)) - 1) / 8) + 1, 6)
      #number
      elif isinstance(operand, int):
        binary += "0"
        binary += decimal_to_binary(math.floor((len(decimal_to_binary(operand)) - 1) / 8) + 1, 6)
      #string
      else:
        binary += "11"
        binary += decimal_to_binary(math.floor(((len(operand) * 8) - 1) / 8) + 1, 5)
    else:
      binary += "0000000"
    #operand_3
    operand_3 = instruction_info[instruction_name]["operand_3"]
    if operand_3 != None:
      operand_3 += 1
      operand = instruction[1][operand_3]
      #register
      if operand in registers.registers:
        binary += "10"
        binary += decimal_to_binary(math.floor((len(decimal_to_binary(int(operand.replace("r", "")))) - 1) / 8) + 1, 5)
      #address
      elif is_valid_address(operand):
        binary += "0"
        binary += decimal_to_binary(math.floor((len(hex_to_binary(operand)) - 1) / 8) + 1, 6)
      #number
      elif isinstance(operand, int):
        binary += "0"
        binary += decimal_to_binary(math.floor((len(decimal_to_binary(operand)) - 1) / 8) + 1, 6)
      #string
      else:
        binary += "11"
        binary += decimal_to_binary(math.floor(((len(operand) * 8) - 1) / 8) + 1, 5)
    else:
      binary += "0000000"
  #no flag
  else:
    #flag
    binary += "0000"
    #instruction
    binary += decimal_to_binary(list(instruction_info.keys()).index(instruction_name), 7)
    #operand_1
    operand_1 = instruction_info[instruction_name]["operand_1"]
    if operand_1 != None:
      operand = instruction[1][operand_1]
      #number
      if isinstance(operand, int):
        binary += "0"
        binary += decimal_to_binary(math.floor((len(decimal_to_binary(operand)) - 1) / 8) + 1, 6)
      #register
      elif "r" in operand:
        binary += "10"
        binary += decimal_to_binary(math.floor((len(decimal_to_binary(int(operand.replace("r", "")))) - 1) / 8) + 1, 5)
      #address
      elif "0x" in operand:
        binary += "0"
        binary += decimal_to_binary(math.floor((len(hex_to_binary(operand)) - 1) / 8) + 1, 6)
      #string
      else:
        binary += "11"
        binary += decimal_to_binary(math.floor(((len(operand) * 8) - 1) / 8) + 1, 5)
    else:
      binary += "0000000"
    #operand_2
    operand_2 = instruction_info[instruction_name]["operand_2"]
    if operand_2 != None:
      operand = instruction[1][operand_2]
      #number
      if isinstance(operand, int):
        binary += "0"
        binary += decimal_to_binary(math.floor((len(decimal_to_binary(operand)) - 1) / 8) + 1, 6)
      #register
      elif "r" in operand:
        binary += "10"
        binary += decimal_to_binary(math.floor((len(decimal_to_binary(int(operand.replace("r", "")))) - 1) / 8) + 1, 5)
      #address
      elif "0x" in operand:
        binary += "0"
        binary += decimal_to_binary(math.floor((len(hex_to_binary(operand)) - 1) / 8) + 1, 6)
      #string
      else:
        binary += "11"
        binary += decimal_to_binary(math.floor(((len(operand) * 8) - 1) / 8) + 1, 5)
    else:
      binary += "0000000"
    #operand_3
    operand_3 = instruction_info[instruction_name]["operand_3"]
    if operand_3 != None:
      operand = instruction[1][operand_3]
      #number
      if isinstance(operand, int):
        binary += "0"
        binary += decimal_to_binary(math.floor((len(decimal_to_binary(operand)) - 1) / 8) + 1, 6)
      #register
      elif "r" in operand:
        binary += "10"
        binary += decimal_to_binary(math.floor((len(decimal_to_binary(int(operand.replace("r", "")))) - 1) / 8) + 1, 5)
      #address
      elif "0x" in operand:
        binary += "0"
        binary += decimal_to_binary(math.floor((len(hex_to_binary(operand)) - 1) / 8) + 1, 6)
      #string
      else:
        binary += "11"
        binary += decimal_to_binary(math.floor(((len(operand) * 8) - 1) / 8) + 1, 5)
    else:
      binary += "0000000"
  binaries.append(binary)
  #operand_1_binary
  if operand_1 != None:
    if binary[11:13] == "10":
      register_number = int(instruction[1][operand_1].replace("r", ""))
      operand_1_binary = decimal_to_binary(register_number, binary_to_decimal(binary[13:18]) * 8)
    else:
      if isinstance(instruction[1][operand_1], str):
        operand_1_binary = ascii_string_to_binary(instruction[1][operand_1], binary_to_decimal(binary[13:18]) * 8, 8)
      else:
        operand_1_binary = decimal_to_binary(instruction[1][operand_1], binary_to_decimal(binary[12:18]) * 8)
    binaries.append(operand_1_binary)
  #operand_2_binary
  if operand_2 != None:
    if binary[18:20] == "10":
      register_number = int(instruction[1][operand_2].replace("r", ""))
      operand_2_binary = decimal_to_binary(register_number, binary_to_decimal(binary[20:25]) * 8)
    else:
      if isinstance(instruction[1][operand_2], str):
        operand_2_binary = ascii_string_to_binary(instruction[1][operand_2], binary_to_decimal(binary[20:25]) * 8, 8)
      else:
        operand_2_binary = decimal_to_binary(instruction[1][operand_2], binary_to_decimal(binary[19:25]) * 8)
    binaries.append(operand_2_binary)
  #operand_3_binary
  if operand_3 != None:
    if binary[25:27] == "10":
      register_number = int(instruction[1][operand_3].replace("r", ""))
      operand_3_binary = decimal_to_binary(register_number, binary_to_decimal(binary[27:32]) * 8)
    else:
      if isinstance(instruction[1][operand_3], str):
        operand_3_binary = ascii_string_to_binary(instruction[1][operand_3], binary_to_decimal(binary[27:32]) * 8, 8)
      else:
        operand_3_binary = decimal_to_binary(instruction[1][operand_3], binary_to_decimal(binary[26:32]) * 8)
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
  for instruction in instructions[:instructions.index("branches:")]:
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
  for instruction in instructions[instructions.index("branches:") + 1:]:
    if instruction[0] == ".":
      branch_name = instruction[1:]
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
  return converted_instructions, converted_branches

def compile_instructions(instruction_stack, tree, address):
  compiled = ""
  binary_instructions = ""
  for instruction in instruction_stack:
    binary_instructions += "".join(instruction_to_binary(instruction))
  compiled += binary_instructions
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

def scan_2_bytes(binary, address):
  scanned = binary_to_ascii_string(binary[address: address + 16])
  return scanned

def run_assembly(address, id):
  #instruction flag [0:4]
  #instruction code [4:11]
  #type of op1 [11:12] OR [11:13] depending on first bit (0x if number, 10 if register, 11 if string)
  #length of op1 [12:18] OR [13:18] depending on type of op1
  #type of op2 [18:19] OR [18:20] depending on first bit (0x if number, 10 if register, 11 if string)
  #length of op2 [19:25] OR [20:25] depending on type of op2
  #type of op3 [25:26] OR [25:27] depending on first bit (0x if number, 10 if register, 11 if string)
  #length of op3 [26:32] OR [27:32] depending on type of op3
  
  global change_current_address, parent_instruction_addresses, current_address, branch_addresses
  joined_ram = "".join(ram)
  #lbr uses the legacy branching system so adding it to this list would break it's usage
  branch_instruction = ["br"]
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
  
  #run through the assembly to find branch addresses
  branch_addresses = {}
  find_branches_address = hex_to_decimal(address)
  scanned = scan_2_bytes(joined_ram, find_branches_address)
  #THERE IS NO BETTER WAY TO DO THIS BECAUSE THERES NO REPEAT UNTIL LOOPS IN PYTHON FUORHGLUIESHUSHRUEHFDKFK
  while not id in terminate_list:
    #incase something breaks and im sleep deprived THIS IS SUPPOSED TO CHECK 0:16 AND INCREMENT BY 8 INCASE THE PARITY IS ODD
    if scanned == "b:":
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
            branch_name += binary_to_ascii(joined_ram[find_branches_address: find_branches_address + 8])
          find_branches_address += 8
          scanned = scan_2_bytes(joined_ram, find_branches_address)
        branch_addresses[branch_name] = find_branches_address
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
  change_current_address = None
  parent_instruction_addresses = []
  current_address = hex_to_decimal(address)
  registers.registers["r15"] = "00000000000000000000000000000000"
  while not id in terminate_list:
    flag = binary_to_decimal(joined_ram[current_address: current_address + 4])
    instruction_name = list(instruction_info.keys())[binary_to_decimal(joined_ram[current_address + 4: current_address + 11])]
    operand_1 = None
    if instruction_info[instruction_name]["operand_1"] != None:
      operand_1_type = joined_ram[current_address + 11: current_address + 13]
      if operand_1_type[0] == "0":
        operand_1_type = "number"
      elif operand_1_type == "10":
        operand_1_type = "register"
      elif operand_1_type == "11":
        operand_1_type = "string"
      else:
        operand_1_type = "number"
      if operand_1_type == "number":
        operand_1_length = binary_to_decimal("".join(joined_ram[current_address + 12: current_address + 18])) * 8
      else:
        operand_1_length = binary_to_decimal("".join(joined_ram[current_address + 13: current_address + 18])) * 8
      if operand_1_type == "register":
        operand_1 = f"r{binary_to_decimal(''.join(joined_ram[current_address + 32: current_address + 32 + operand_1_length]))}"
      elif operand_1_type == "number":
        operand_1 = binary_to_decimal("".join(joined_ram[current_address + 32: current_address + 32 + operand_1_length]))
      elif operand_1_type == "string":
        operand_1 = binary_to_ascii_string("".join(joined_ram[current_address + 32: current_address + 32 + operand_1_length]))
    else:
      operand_1_length = 0
    operand_2 = None
    if instruction_info[instruction_name]["operand_2"] != None:
      operand_2_type = joined_ram[current_address + 18: current_address + 20]
      if operand_2_type[0] == "0":
        operand_2_type = "number"
      elif operand_2_type == "10":
        operand_2_type = "register"
      elif operand_2_type == "11":
        operand_2_type = "string"
      else:
        operand_2_type = "number"
      if operand_2_type == "number":
        operand_2_length = binary_to_decimal("".join(joined_ram[current_address + 19: current_address + 25])) * 8
      else:
        operand_2_length = binary_to_decimal("".join(joined_ram[current_address + 20: current_address + 25])) * 8
      if operand_2_type == "register":
        operand_2 = f"r{binary_to_decimal(''.join(joined_ram[current_address + 32 + operand_1_length: current_address + 32 + operand_1_length + operand_2_length]))}"
      elif operand_2_type == "number":
        operand_2 = binary_to_decimal("".join(joined_ram[current_address + 32 + operand_1_length: current_address + 32 + operand_1_length + operand_2_length]))
      elif operand_2_type == "string":
        operand_2 = binary_to_ascii_string("".join(joined_ram[current_address + 32 + operand_1_length: current_address + 32 + operand_1_length + operand_2_length]))
    else:
      operand_2_length = 0
    operand_3 = None
    if instruction_info[instruction_name]["operand_3"] != None:
      operand_3_type = joined_ram[current_address + 25: current_address + 27]
      if operand_3_type[0] == "0":
        operand_3_type = "number"
      elif operand_3_type == "10":
        operand_3_type = "register"
      elif operand_3_type == "11":
        operand_3_type = "string"
      else:
        operand_3_type = "number"
      if operand_3_type == "number":
        operand_3_length = binary_to_decimal("".join(joined_ram[current_address + 26: current_address + 32])) * 8
      else:
        operand_3_length = binary_to_decimal("".join(joined_ram[current_address + 27: current_address + 32])) * 8
      if operand_3_type == "register":
        operand_3 = f"r{binary_to_decimal(''.join(joined_ram[current_address + 32 + operand_1_length + operand_2_length: current_address + 32 + operand_1_length + operand_2_length + operand_3_length]))}"
      elif operand_3_type == "number":
        operand_3 = binary_to_decimal("".join(joined_ram[current_address + 32 + operand_1_length + operand_2_length: current_address + 32 + operand_1_length + operand_2_length + operand_3_length]))
      elif operand_3_type == "string":
        operand_3 = binary_to_ascii_string("".join(joined_ram[current_address + 32 + operand_1_length + operand_2_length: current_address + 32 + operand_1_length + operand_2_length + operand_3_length]))
    else:
      operand_3_length = 0
    if flag > 0:
      if flags[list(flags.keys())[flag - 1]] == "0":
        if change_current_address != None:
          current_address = change_current_address
          change_current_address = None
        else:
          current_address += 32 + operand_1_length + operand_2_length + operand_3_length
        continue
    if instruction_name in branch_addresses:
      registers.registers["r15"] = branch_addresses[branch]
    else:
      registers.registers["r15"] = decimal_to_binary(current_address + 32 + operand_1_length + operand_2_length + operand_3_length, 32)
    instruction_info[instruction_name]["function"](*[i for i in [operand_1, operand_2, operand_3] if i != None])
    if instruction_name == "syscall" and operand_2 == 0:
      break
    if change_current_address != None:
      current_address = change_current_address
      change_current_address = None
    else:
      current_address += 32 + operand_1_length + operand_2_length + operand_3_length
  if id in terminate_list:
    terminate_list.remove(id)

def event_handler():
  global text, terminate, terminate_list, ids, storage
  
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
    if tokens[0] == "run":
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
              ram[hex_to_decimal(tokens[4]) + increment] = value

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
      text.place_configure(y=screen_height - text.winfo_height() - 38)
    else:
      text.place_configure(y=screen_height - text.winfo_height() - 21)

def prepare_os():
  global configuration, registers, flags, instruction_info, data, ram, storage, text_input_queue, terminate, terminate_list, ids
  #None = unused
  #Number (0, 1, 2...) = index of arguments where this is found
  #operand_1 is store, operand_2 is the main operand, operand_3 is the info
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
    "strr": {
      "operand_1": 0,
      "operand_2": 1,
      "operand_3": None,
      "function": strr,
      "flag_function": strrflag
    },
    "strs": {
      "operand_1": 0,
      "operand_2": 1,
      "operand_3": None,
      "function": strs,
      "flag_function": strsflag
    },
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
    "lbr": {
      "operand_1": None,
      "operand_2": 0,
      "operand_3": None,
      "function": lbr,
      "flag_function": lbrflag
    },
    "br": {
      "operand_1": None,
      "operand_2": 0,
      "operand_3": None,
      "function": br,
      "flag_function": brflag
    },
    "bl": {
      "operand_1": None,
      "operand_2": 0,
      "operand_3": None,
      "function": bl,
      "flag_function": blflag
    },
    "push": {
      "operand_1": None,
      "operand_2": 0,
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
      "operand_1": None,
      "operand_2": 0,
      "operand_3": None,
      "function": syscall,
      "flag_function": syscallflag
    },
    "ws": {
      "operand_1": None,
      "operand_2": None,
      "operand_3": None,
      "function": ws,
      "flag_function": wsflag
    }
  }

  try:
    configuration_file = open("pythos.cfg", "r")
  except:
    create_configuration_file = open("pythos.cfg", "x")
    create_configuration_file.close()
    configuration_file = open("pythos.cfg", "w")
    #1 mib default
    configuration = {
      "version": "0.0.0",
      "storage_size": 1048576,
      "ram_size": 1048576
    }
    configuration_file.write(str(configuration))
    configuration_file.close()
  else:
    configuration = ast.literal_eval(configuration_file.read())

  registers = threading.local()
  flags = threading.local()

  ram = []
  for increment in range(configuration["ram_size"]):
    ram.append("00000000")

  storage = []
  for increment in range(configuration["storage_size"]):
    storage.append("00000000")
  try:
    true_storage = open("storage.psb", "r")
  except:
    create_storage_file = open("storage.psb", "x")
    create_storage_file.close()
    true_storage = open("storage.psb", "r")
  read = true_storage.read()
  if read == "":
    write_storage()
  if input("Empty storage? (Y/n)\n").lower() == "y":
    write_storage()
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
  text_input_queue = None
  terminate = False
  terminate_list = []
  ids = []
  event_thread = threading.Thread(target=event_handler, daemon=True)
  event_thread.start()
  tkinter_thread = threading.Thread(target=tkinter_handler, daemon=True)
  tkinter_thread.start()



def update_text_with_key(key):
  global text_input_queue, terminate
  text_input_queue = key.char
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



def mov(register, info):
  if isinstance(info, int):
    registers.registers[register] = decimal_to_binary(info, 32)
  elif info in registers.registers:
    registers.registers[register] = registers.registers[info]
  elif "0x" in info:
    registers.registers[register] = ram[hex_to_decimal(info.replace("0x", ""))]

def movflag(flag, register, info):
  if flags[flag] == "1":
    mov(register, info)


#load ram
def ldrr(register, label):
  if "0x" in label:
    registers.registers[register] = decimal_to_binary(binary_to_decimal(ram[hex_to_decimal(label.replace("0x", ""))]), 32)
  else:
    registers.registers[register] = decimal_to_binary(binary_to_decimal(ram[binary_to_decimal(registers.registers[label])]), 32)

def ldrrflag(flag, register, label):
  if flags[flag] == "1":
    ldrr(register, label)


#load storage
def ldrs(register, label):
  if "0x" in label:
    registers.registers[register] = decimal_to_binary(binary_to_decimal(storage[hex_to_decimal(label.replace("0x", ""))]), 32)
  else:
    registers.registers[register] = decimal_to_binary(binary_to_decimal(storage[hex_to_decimal(registers.registers[label])]), 32)

def ldrsflag(flag, register, label):
  if flags[flag] == "1":
    ldrs(register, label)


#store ram
def strr(label, store_label):
  register_size = math.ceil(len(registers.registers[label]) / 8)
  if "0x" in store_label:
    for increment in range(register_size):
      ram[(hex_to_decimal(store_label.replace("0x", "")) * 4) + increment] = registers.registers[label][increment * 8: (increment * 8) + 8]
  else:
    for increment in range(register_size):
      ram[(binary_to_decimal(registers.registers[store_label]) * 4) + increment] = registers.registers[label][increment * 8: (increment * 8) + 8]

def strrflag(flag, label, store_label):
  if flags[flag] == "1":
    strr(label, store_label)


#store storage
def strs(register, store_label):
  register_size = math.ceil(len(registers.registers[register]) / 8)
  if "0x" in store_label:
    for increment in range(register_size):
      storage[(hex_to_decimal(store_label.replace("0x", "")) * 4) + increment] = registers.registers[register][increment * 8: (increment * 8) + 8]
  else:
    for increment in range(register_size):
      storage[(binary_to_decimal(registers.registers[store_label]) * 4) + increment] = registers.registers[register][increment * 8: (increment * 8) + 8]

def strsflag(flag, register, store_label):
  if flags[flag] == "1":
    strs(register, store_label)


def add(store_register, register, info):
  if isinstance(info, int):
    sum = binary_to_decimal(registers.registers[register]) + info
    update_cpsr(register, sum)
  elif "r" in info:
    sum = binary_to_decimal(registers.registers[register]) + binary_to_decimal(registers.registers[info])
    update_cpsr(register, sum)
  elif "0x" in info:
    sum = binary_to_decimal(registers.registers[register]) + binary_to_decimal(ram[hex_to_decimal(info.replace("0x", ""))])
    update_cpsr(register, sum)
  if store_register != None:
    registers.registers[store_register] = decimal_to_binary(sum, 32)

def addflag(flag, store_register, register, info):
  if flags[flag] == "1":
    add(store_register, register, info)


def sub(store_register, register, info):
  if isinstance(info, int):
    difference = binary_to_decimal(registers.registers[register]) - info
    update_cpsr(register, difference)
  elif "r" in info:
    difference = binary_to_decimal(registers.registers[register]) - binary_to_decimal(registers.registers[info])
    update_cpsr(register, difference)
  elif "0x" in info:
    difference = binary_to_decimal(registers.registers[register]) - binary_to_decimal(hex_to_decimal(info.replace("0x", "")))
    update_cpsr(register, difference)
  if store_register:
    registers.registers[store_register] = decimal_to_binary(difference, 32)

def subflag(flag, store_register, register, info):
  if flags[flag] == "1":
    sub(store_register, register, info)


def mul(store_register, register, info):
  if isinstance(info, int):
    multiplied = binary_to_decimal(registers.registers[register]) * info
    update_cpsr(register, multiplied)
  elif "r" in info:
    multiplied = binary_to_decimal(registers.registers[register]) * binary_to_decimal(registers.registers[info])
    update_cpsr(register, multiplied)
  elif "0x" in info:
    multiplied = binary_to_decimal(registers.registers[register]) * binary_to_decimal(hex_to_decimal(info.replace("0x", "")))
    update_cpsr(register, multiplied)
  if store_register:
    registers.registers[store_register] = decimal_to_binary(multiplied, 32)

def mulflag(flag, store_register, register, info):
  if flags[flag] == "1":
    mul(store_register, register, info)


def cmp(register, info):
  sub(None, register, info)
  flag_set = False
  if registers.registers["cpsr"][1] == "1":
    flag_set = True
    flags["EQ"] = "1"
  else:
    flags["EQ"] = "0"
  if registers.registers["cpsr"][1] == "0":
    flag_set = True
    flags["NE"] = "1"
  else:
    flags["NE"] = "0"
  if registers.registers["cpsr"][1] == "0" and registers.registers["cpsr"][0] == registers.registers["cpsr"][3]:
    flag_set = True
    flags["GT"] = "1"
  else:
    flags["GT"] = "0"
  if registers.registers["cpsr"][0] != registers.registers["cpsr"][3]:
    flag_set = True
    flags["LT"] = "1"
  else:
    flags["LT"] = "0"
  if registers.registers["cpsr"][0] == registers.registers["cpsr"][3]:
    flag_set = True
    flags["GE"] = "1"
  else:
    flags["GE"] = "0"
  if registers.registers["cpsr"][1] == "1" or registers.registers["cpsr"][0] != registers.registers["cpsr"][3]:
    flag_set = True
    flags["LE"] = "1"
  else:
    flags["LE"] = "0"
  if registers.registers["cpsr"][2] == "1":
    flag_set = True
    flags["CS"] = "1"
  else:
    flags["CS"] = "0"
  if registers.registers["cpsr"][2] == "0":
    flag_set = True
    flags["CC"] = "1"
  else:
    flags["CC"] = "0"
  if registers.registers["cpsr"][0] == "1":
    flag_set = True
    flags["MI"] = "1"
  else:
    flags["MI"] = "0"
  if registers.registers["cpsr"][0] == "0":
    flag_set = True
    flags["PL"] = "1"
  else:
    flags["PL"] = "0"
  #what is this flag
  flags["NV"] = "0"
  if registers.registers["cpsr"][3] == "1":
    flag_set = True
    flags["VS"] = "1"
  else:
    flags["VS"] = "0"
  if registers.registers["cpsr"][3] == "0":
    flag_set = True
    flags["VC"] = "1"
  else:
    flags["VC"] = "0"
  if registers.registers["cpsr"][2] == "1" and registers.registers["cpsr"][1] == "0":
    flag_set = True
    flags["HI"] = "1"
  else:
    flags["HI"] = "0"
  if registers.registers["cpsr"][2] == "0" or registers.registers["cpsr"][1] == "0":
    flag_set = True
    flags["LS"] = "1"
  else:
    flags["LS"] = "0"
  if not flag_set:
    flags["AL"] = "1"
  else:
    flags["AL"] = "0"

def cmpflag(flag, register, info):
  if flags[flag] == "1":
    cmp(register, info)


#legacy branch, DO NOT USE UNLESS USING INSTRUCTION STACK
def lbr(branch):
  del instruction_stack[1:]
  for instruction in branches[branch]:
    instruction_stack.append(instruction)

def lbrflag(flag, branch):
  if flags[flag] == "1":
    lbr(branch)


def br(branch):
  global change_current_address
  change_current_address = branch_addresses[branch]

def brflag(flag, branch):
  if flags[flag] == "1":
    br(branch)


def bl(branch):
  global change_current_address, parent_instruction_addresses
  #for convenience purposes since removing this would possibly break a couple of programs when trying to go up multiple parents
  parent_instruction_addresses.insert(0, current_address + 32 + len(ascii_string_to_binary(branch, None, 8)))
  registers.registers["r14"] = current_address + 32 + len(ascii_string_to_binary(branch, None, 8))
  change_current_address = branch_addresses[branch]

def blflag(flag, branch):
  if flags[flag] == "1":
    bl(branch)


def jmp(address):
  global change_current_address
  change_current_address = address

def jmpflag(flag, address):
  if flags[flag] == "1":
    jmp(address)


def push(register):
  registers.registers["r13"] = decimal_to_binary(binary_to_decimal(registers["r13"]) - 4, 32)
  #because of how python's indexing works (starts at 0), these must be shifted back one to offset for the sp being 128 rather than 127
  ram[binary_to_decimal(registers.registers["r13"]) - 4] = registers.registers[register][0:8]
  ram[binary_to_decimal(registers.registers["r13"]) - 3] = registers.registers[register][8:16]
  ram[binary_to_decimal(registers.registers["r13"]) - 2] = registers.registers[register][16:24]
  ram[binary_to_decimal(registers.registers["r13"]) - 1] = registers.registers[register][24:32]

def pushflag(flag, register):
  if flags[flag] == "1":
    push(register)


def pop(register):
  registers.registers[register] = "".join(ram[binary_to_decimal(registers.registers["r13"]) - 4: binary_to_decimal(registers.registers["r13"])])
  ram[binary_to_decimal(registers.registers["r13"]) - 4: binary_to_decimal(registers.registers["r13"])] = ["00000000", "00000000", "00000000", "00000000"]
  registers.registers["r13"] = decimal_to_binary(binary_to_decimal(registers.registers["r13"]) + 4, 32)

def popflag(flag, register):
  if flags[flag] == "1":
    pop(register)


def syscall(call):
  #syscall 0 is an exit
  #print ascii representation of r12
  if call == 1:
    global text
    text["text"] += binary_to_ascii(registers.registers["r12"])
  #check for input and put it into r12
  if call == 2:
    global text_input_queue
    if text_input_queue:
      registers.registers["r12"] = ascii_to_binary(text_input_queue, 32)
      text_input_queue = None
    else:
      registers.registers["r12"] = "00000000000000000000000000000000"
  #return to parent branch
  elif call == 3:
    global change_current_address, parents_instruction_addresses
    change_current_address = parent_instruction_addresses.pop(0)

def syscallflag(flag, call):
  if flags[flag] == "1":
    syscall(call)


def ws():
  write_storage()

def wsflag(flag):
  if flags[flag] == "1":
    ws()



prepare_os()

special_keys = ["\r", "\x08", "\x03"]
main_window = Tk()

main_window["background"] = "black"
main_window.geometry(f"{main_window.winfo_screenwidth()}x{main_window.winfo_screenheight()}")
text = Label(main_window, text="", foreground="white", background="black")
text.place(x=0, y=0, anchor=NW)
main_window.bind("<KeyPress>", update_text_with_key)
mainloop()