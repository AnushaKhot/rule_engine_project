import re

# Define the Node class to represent AST nodes
class Node:
    def __init__(self, type, value=None, left=None, right=None):
        self.type = type  # 'operator' for AND/OR, 'operand' for conditions
        self.value = value  # condition or operator (e.g., 'age > 30', 'AND')
        self.left = left  # Left child (another Node)
        self.right = right  # Right child (another Node)

# Function to parse a rule string and build an AST
def create_rule(rule_string):
    tokens = tokenize_rule(rule_string)
    ast = parse_tokens(tokens)
    return ast

# Tokenize the rule string
def tokenize_rule(rule_string):
    # Modify the regex to tokenize conditions as single items (e.g., 'age > 30')
    return re.findall(r'\(|\)|[A-Za-z_]+(?: [<>=!]+ [0-9A-Za-z_\']+)?|AND|OR', rule_string)

# Parse tokens to create the AST
def parse_tokens(tokens):
    # Stack for building the AST
    node_stack = []
    operator_stack = []

    # Operator precedence
    precedence = {'OR': 1, 'AND': 2}

    def apply_operator():
        right = node_stack.pop()
        left = node_stack.pop()
        operator = operator_stack.pop()
        node_stack.append(Node('operator', operator, left, right))

    i = 0
    while i < len(tokens):
        token = tokens[i]

        if token == '(':
            operator_stack.append(token)
        elif token == ')':
            while operator_stack and operator_stack[-1] != '(':
                apply_operator()
            operator_stack.pop()  # Pop the '('
        elif token in ['AND', 'OR']:
            while (operator_stack and operator_stack[-1] in precedence and
                   precedence[operator_stack[-1]] >= precedence[token]):
                apply_operator()
            operator_stack.append(token)
        elif re.match(r"\w+ [<>=!]+ .+", token):  # Base condition
            node_stack.append(Node('operand', token))
        i += 1

    while operator_stack:
        apply_operator()

    return node_stack[0]

# Function to combine multiple rules into one AST
def combine_rules(rules):
    asts = [create_rule(rule) for rule in rules]
    combined_ast = asts[0]

    # Combine rules using AND (You can modify this logic for other combinations)
    for ast in asts[1:]:
        combined_ast = Node('operator', 'AND', combined_ast, ast)

    return combined_ast

# Function to evaluate a rule's AST against user data
def evaluate_rule(ast_node, data):
    # If the node is an operator, recursively evaluate left and right nodes
    if ast_node.type == 'operator':
        left_value = evaluate_rule(ast_node.left, data)
        right_value = evaluate_rule(ast_node.right, data)

        # Evaluate based on the operator type (AND/OR)
        if ast_node.value == 'AND':
            return left_value and right_value
        elif ast_node.value == 'OR':
            return left_value or right_value

    # If the node is an operand (base condition), evaluate the condition
    elif ast_node.type == 'operand':
        return eval_condition(ast_node.value, data)

    return False

# Function to evaluate a base condition like 'age > 30'
def eval_condition(condition, data):
    print(f"Evaluating condition: {condition}")  # Debug line

    # Regular expression to capture field, operator, and value
    match = re.match(r"(\w+) ([<>=!]+) (.+)", condition)
    if match is None:
        raise ValueError(f"Invalid condition format: {condition}")

    field, operator, value = match.groups()

    # Ensure the field exists in the data dictionary
    if field in data:
        if operator == '>':
            return data[field] > int(value)
        elif operator == '<':
            return data[field] < int(value)
        elif operator == '>=':
            return data[field] >= int(value)
        elif operator == '<=':
            return data[field] <= int(value)
        elif operator == '==':
            return str(data[field]) == value.strip("'")
        elif operator == '!=':
            return str(data[field]) != value.strip("'")
    
    return False

# Test cases

# Sample rules
rule1 = "((age > 30 AND department == 'Sales') OR (age < 25 AND department == 'Marketing')) AND (salary > 50000 OR experience > 5)"
rule2 = "((age > 30 AND department == 'Marketing')) AND (salary > 20000 OR experience > 5)"

# Sample user data
data_sample = {
    "age": 35,
    "department": "Sales",
    "salary": 60000,
    "experience": 3
}

# Step 1: Create individual ASTs for each rule
ast_rule1 = create_rule(rule1)
ast_rule2 = create_rule(rule2)

# Step 2: Combine rules into a single AST
combined_ast = combine_rules([rule1, rule2])

# Step 3: Evaluate the rules against the data
print(evaluate_rule(ast_rule1, data_sample))  # Expected output: True (based on sample data)
print(evaluate_rule(ast_rule2, data_sample))  # Expected output: False (since department is 'Sales')

# Evaluate the combined AST
print(evaluate_rule(combined_ast, data_sample))  # Expected output: False (as rule2 doesn't match)
