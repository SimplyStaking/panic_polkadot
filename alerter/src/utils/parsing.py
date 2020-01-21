# This function takes an integer represented as string (can be both hex and dec)
# Note: This function works for Hex if the value is expressed as
#       0xRemainingHexDigits
def parse_int_from_string(val: str) -> int:
    if "0x" in val:
        return int(val, 16)
    else:
        return int(val)
