import re

class VariableManager:
    def __init__(self):
        self.variables = {}

    def replace_variables(self, text):
        """Replace occurrences of $varname with their values, ensuring proper isolation."""
        def var_replacer(match):
            var_name = match.group(1)
            return str(self.variables.get(var_name, f"${var_name}"))
        
        return re.sub(r"\$(\w+)", var_replacer, text)

    def set_variable(self, line):
        """Parse and store a variable, supporting arithmetic and string concatenation operations."""
        match = re.match(r"(setvar|gsetvar) (\w+)\s*(==|[+\-*/])\s*(.+)", line)
        if match:
            _, var_name, operator, value = match.groups()
            try:
                value = int(value)
            except ValueError:
                value = value.strip('"')
            if var_name not in self.variables:
                self.variables[var_name] = 0 if isinstance(value, int) else ""

    def set_variables(self, line):
        """Parse and store a variable, supporting arithmetic and string concatenation operations."""
        match = re.match(r"(setvar|gsetvar) (\w+)\s*(==|[+\-*/])\s*(.+)", line)
        if match:
            _, var_name, operator, value = match.groups()
            try:
                value = int(value)
            except ValueError:
                value = value.strip('"')
            if var_name not in self.variables:
                self.variables[var_name] = 0 if isinstance(value, int) else ""
            if operator == "==":
                self.variables[var_name] = value
            elif isinstance(self.variables[var_name], int) and isinstance(value, int):
                if operator == "+":
                    self.variables[var_name] += value
                elif operator == "-":
                    self.variables[var_name] -= value
            elif isinstance(self.variables[var_name], str) and isinstance(value, str):
                if operator == "+":
                    self.variables[var_name] += value