import math

ascii_characters = ["", "", "", "", "", "", "", "", "", "  ", "\n", "", "", "\r", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", " ", "!", '"', "#", "$", "%", "&", "'", "(", ")", "*", "+", ",", "-", ".", "/", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", ":", ";", "<", "=", ">", "?", "@", "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z", "[", "\\", "]", "^", "_", "`", "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", "{", "|", "}", "~", ""]
hex_characters = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "A", "B", "C", "D", "E", "F"]

def hex_to_decimal(hex):
  decimal = 0
  increment = 1
  for hex_character in hex[::-1]:
    decimal += hex_characters.index(hex_character) * increment
    increment *= 16
  return decimal

def decimal_to_hex(decimal):
  hex = ""
  #to prevent an infinite loop, this is capped to 128 hex characters
  for increment in range(128):
    if decimal < pow(16, increment):
      break
    else:
      hex += hex_characters[math.floor(decimal / pow(16, increment)) % 16]
  return hex[::-1]

def hex_to_binary(hex, length=None):
  return decimal_to_binary(hex_to_decimal(hex), length)

def decimal_to_binary(decimal, length=None):
  binary = "{0:b}".format(abs(decimal))
  if length == None:
    return binary
  if len(binary) > length:
    raise Exception("Binary length exceeded specified length!")
  elif len(binary) < length:
    buffer = ""
    for increment in range(length - len(binary)):
      buffer += "0"
    binary = f"{buffer}{binary}"
  return binary

def binary_to_decimal(binary):
  reversed_binary = binary[::-1]
  decimal = 0
  for increment, bit in enumerate(reversed_binary):
    if bit == "1":
      decimal += pow(2, increment)
  return decimal

def binary_to_ascii(binary):
  try:
    return ascii_characters[binary_to_decimal(binary)]
  except:
    return ""

def ascii_to_binary(ascii, length=None):
  if not ascii in ascii_characters:
    return decimal_to_binary(0, length)
  return decimal_to_binary(ascii_characters.index(ascii), length)

def ascii_string_to_binary(ascii, string_length=None, character_length=None):
  binaries = [ascii_to_binary(i, character_length) for i in ascii]
  binary = "".join(binaries)
  if string_length == None:
    return binary
  if len(binary) > string_length:
    raise Exception("Binary length exceeded specified length!")
  buffer = ""
  for increment in range(string_length - len(binary)):
    buffer += "0"
  binary = f"{buffer}{binary}"
  return binary

def binary_to_ascii_string(binary):
  binaries = [binary[i:i + 8] for i in range(0, len(binary), 8)]
  characters = [binary_to_ascii(i) for i in binaries]
  return "".join(characters)