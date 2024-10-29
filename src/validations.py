class ValidationException(Exception):
     # Constructor or Initializer
    def __init__(self, value):
        self.value = value
 
    # __str__ is to print() the value
    def __str__(self):
        return(repr(self.value))

def isNotEmpty(s: str, param_name: str):
    if s is None or s.strip() == "":
        #alert(f"{param_name} is empty or None.", "Error")
        raise ValidationException(f"{param_name} is empty or None.")
    return True

def isInt(s: str, param_name: str):
    if isNotEmpty(s, param_name) and not s.isdigit():
        #alert("Invalid value for {param_name}.", "Error")
        raise ValidationException(f"{param_name} is not an integer value.")
    return True

def isFloat(s: str, param_name: str):
    if isNotEmpty(s, param_name):
        try:
            float(s)
        except ValueError:
            #alert("Invalid value for {param_name}.", "Error")
            raise ValidationException(f"{param_name} is not a float value.")
    return True
