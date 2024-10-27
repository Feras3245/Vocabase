from Linguee_Scraper import *
from Notion_API_Handler import Notion_API_Handler
import sys
import getopt

os.system("")


# flags keep white along with (description)
#  # green, yellow, red, magenta, cyan
# "(print error messages?)"

def prompt_yes_no(question: str) -> bool:
    try_again = True
    while try_again:
        usr_input = input(change_text_color(question + ' ', 'cyan', 'keep'))
        usr_input = usr_input.lower().strip()
        # regex = r'^(?:\s*)yes(?:\s*)$|ye(?:\s*)$|y(?:\s*)$|no(?:\s*)$|n(?:\s*)$'
        # matches = re.findall(regex, usr_input, re.IGNORECASE)
        if usr_input in ('yes', 'ye', 'y'):
            return True
        elif usr_input in ('no', 'n'):
            return False
        else:
            print(change_text_color('INPUT ERROR: ', 'red', 'keep') + "please try again...")
            try_again = True

def prompt_operations(results: list, notion: Notion_API_Handler):
    for index, result in enumerate(results):
        alphabet = string.ascii_uppercase
        title = bold_text(change_text_color(" Table: ", 'black', 'white')) + bold_text(change_text_color(f"  {alphabet[index]}  ", 'white', 'blue'))
        print(title+'\u001b[30m\u001b[47m')
        print_result(result)
        print('\u001b[0m')
    parser_help_guide()

    print("Enter" + bold_text(change_text_color(" Any Whitespace Character ", 'blue', 'keep')) + "To Enter Another Query")

    operation = input(change_text_color("Operation: ", 'Magenta', 'keep'))

    if operation.isspace():
        return
    
    clause, sub_operation = parse_op(operation)

    if clause == 'unrecognized':
        print(change_text_color('PARSING ERROR: ', 'red', 'keep') + 'unrecognizable operation')
        print()
        prompt_operations(results, notion)
        return
    
    elif clause == 'insert':
        success, content = insert_op(sub_operation, results)
        if success:
            commit = prompt_yes_no('Commit (y/n)?')
            if commit == True:
                results = content
                for result in results:
                    insertion_success = notion.insert_notion_row(result)
                    while not insertion_success:
                        print(change_text_color("Failure!", 'red', 'keep') + " failed to insert row!")
                        try_again = prompt_yes_no('Attempt Insertion Again (y/n)?')
                        if try_again:
                            insertion_success = notion.insert_notion_row(results)
                        else:
                            break
                    if insertion_success:
                        print(change_text_color("Success!", 'green', 'keep') + " successfully inserted row!")
            return

        else:
            print(change_text_color('INSERT ERROR: ', 'red', 'keep') + content)
            print()
            prompt_operations(results, notion)
            return

    elif clause == 'drop':
        success, content = drop_op(sub_operation, results)
        if success:
            if (content == None) or (len(content) == 0):
                print()
                print('No tables left...')
                return
            else:
                print(change_text_color("Success!", 'green', 'keep') + " successfully dropped table(s)!")
                print()
                prompt_operations(content, notion)
                return
        else:
            print(change_text_color('DROP ERROR: ', 'red', 'keep') + content)
            print()
            prompt_operations(results, notion)
            return

    elif clause == 'edit':
        success, content = edit_op(sub_operation, results)
        if success:
            print()
            prompt_operations(content, notion)
            return
        else:
            print(change_text_color('EDIT ERROR: ', 'red', 'keep') + content)
            print()
            prompt_operations(results, notion)
            return
    return


def cli_args_parser():
    help_message = "\n" + bold_text(change_text_color("vocabase.py", 'magenta', 'leave')) + " -n " + change_text_color("<niveau> ", 'yellow', 'leave') + "-w " + change_text_color("<week> ", 'cyan', 'leave') + "-b " + change_text_color("(fetch only best result?) ", 'green', 'leave') + "-e " + change_text_color("(print error messages?) ", 'red', 'leave') + "\n"
    help_message += change_text_color("<niveau>", 'yellow', 'leave') + bold_text(" --> ") + "desired language level page on Notion e.g. A1.2, A2.1, B2.2, etc.\n"
    help_message += change_text_color("<week>", 'cyan', 'leave') + bold_text(" --> ") + "desired week page in the nivea page on Notion e.g. (1: week 1), (2: week 2), etc.\n"
    help_message += change_text_color("(fetch only best result?)", 'green', 'leave') + bold_text(" --> ") + "if set, only best (featured) result will be fetched.\n"
    help_message += change_text_color("(print error messages?)", 'red', 'leave') + bold_text(" --> ") + "if set, non-critical error messages will be printed when they occur.\n"

    flags, args = getopt.getopt(sys.argv[1:], 'hn:w:be', ['help', 'niveau=', 'week=', 'best', 'errors'])
    ret_vals = {}
    for flag, arg in flags:
        if flag in ('-h', '--help'):
            print(help_message)
            sys.exit(0)
        elif flag in ('-n', '--niveau'):
            if not (arg == ''):
                ret_vals['niveau'] = arg
        elif flag in ('-w', '--week'):
            if not (arg == ''):
                ret_vals['week'] = arg
        elif flag in ('-b', '--best'):
            ret_vals['best_only'] = True
        elif flag in ('-e', '--errors'):
            ret_vals['print_errors'] = True
    if len(args) != 0:
        for arg in args:
            if validate_niveau(arg.strip()):
                ret_vals['niveau'] = arg
            elif arg.isdecimal():
                ret_vals['week'] = arg
    return ret_vals

def validate_niveau(niveau: str) -> bool:
    pattern = r'^\b[ABCabc][12].[12]\b$'
    niveau = niveau.strip()
    if bool(re.match(pattern, niveau)):
        return True
    else:
        return False

def parser_help_guide():
    print(bold_text(change_text_color("Operations: ", 'magenta', 'keep')), "insert, edit, drop")
    print(change_text_color("insert", 'green', 'keep') + "  <" + change_text_color("table(s)", 'yellow', 'keep') + 
          ' or ' + change_text_color("all", 'yellow', 'keep') + '> ')
    print(change_text_color("edit", 'blue', 'keep') + "  <" + change_text_color("table", 'yellow', 'keep') +
        '> ' + " <" + change_text_color("property", 'yellow', 'keep') + '> ' + " [" + 
        change_text_color("+", 'green', 'keep') + " or " + change_text_color("-", 'green', 'keep') + '] ' + 
        " [(for " + change_text_color("+", 'green', 'keep') + " -> {" + 
        change_text_color("new entry", 'cyan', 'keep') + "}) (for "+ change_text_color("-", 'green', 'keep') + " -> {" + 
        change_text_color("old entry number(s)", 'cyan', 'keep') + "})]")
    print(change_text_color("drop", 'red', 'keep') + "  <" + change_text_color("table(s)", 'yellow', 'keep') + ' or ' + change_text_color("all", 'yellow', 'keep') + '> ')
    print("in case of " + change_text_color("edit", 'blue', 'keep') + " place non numeric values between \"double quotes\", and separate them with ','")
    
def parse_op(op: str):
    lower_op = op.lower()
    # The type of operation must be the first word in the op string
    # it can be perceded only by whitespaces
    regex = r"^(?:\s*)(insert|drop|edit)\b"
    matches = re.findall(regex, lower_op, re.IGNORECASE)
    if not bool(re.match(regex, lower_op)):
        return "unrecognized", None
    # if the function is still executing that means that the string begins with one of the operation words
    # and only one operation word is within the op string
    operation_type = matches[0].strip().lower()
    # we now need a new string that does not contain the part that has been processed
    sub_op = op[len(matches[0]):]
    # the parsing of the rest of the string depends on the type of operation to be performed
    return operation_type, sub_op


def insert_op(sub_op: str, results: list):
    alphabet = string.ascii_uppercase
    len_results = len(results)
    output = []
    # the rest of the substring can either be 'all' but it has to be all by itself
    # or whitespace separated table cyphers
    regex = r"(^(?:\s*)all(?:\s*)$)|(^((?:\s*)\b[a-zA-Z]\b(?:\s*))+$)"
    if not bool(re.match(regex, sub_op)):
        msg = "unrecognized table symbol(s)."
        return False, msg
    
    # if all return results in full for insertion
    regex = r"^(?:\s*)all(?:\s*)$"
    if bool(re.match(regex, sub_op)):
        return True, results
    # if all is not found it could either mean that
    # we have a list of tables separated by whitespace characters
    # pr the user has entered random input
    regex = r"^((?:\s*)\b[a-zA-Z]\b(?:\s*))+$"
    matches = re.findall(regex, sub_op, re.IGNORECASE)
    if not matches:
        # if anything other than single letters separated by whitespaces
        # is found, then the operation is unrecognized
        msg = "unknown keyword detected."
        return False, msg
    regex = r'\b[a-zA-Z]\b'
    matches = re.findall(regex, sub_op, re.IGNORECASE)
    tables = matches
    # if that is not the case, then it is a valid list of table symbols
    insert_indexes = []
    for table in tables:
        table = table.strip().upper()
        table_index = alphabet.find(table)
        if (table_index >= 0) and (table_index < len_results):
            insert_indexes.append(table_index)
        else:
            print(change_text_color("NON-CRITICAL ERROR: ", 'red', 'keep') + "Table " + bold_text(change_text_color(f"{table}", 'blue', 'keep')) + " not found in results!")
    if insert_indexes != 0:
        for insert_index in insert_indexes:
            output.append(results[insert_index])
        return True, output
    else:
        msg = 'no tables to insert'
        return False, msg

def drop_op(sub_op: str, results: list):
    alphabet = string.ascii_uppercase
    len_results = len(results)
    output = []
    # the rest of the substring can either be 'all' but it has to be all by itself
    # or whitespace separated table cyphers
    regex = r"(^(?:\s*)all(?:\s*)$)|(^((?:\s*)\b[a-zA-Z]\b(?:\s*))+$)"
    if not bool(re.match(regex, sub_op)):
        msg = 'unrecognized table symbol(s)'
        return False, msg 
    
    # if all return results in full for insertion
    regex = r"^(?:\s*)all(?:\s*)$"
    matches = re.findall(regex, sub_op, re.IGNORECASE)
    if matches:
        return True, None
    # if all is not found it could either mean that
    # we have a list of tables separated by whitespace characters
    # pr the user has entered random input
    regex = r"^((?:\s*)\b[a-zA-Z]\b(?:\s*))+$"
    matches = re.findall(regex, sub_op, re.IGNORECASE)
    if not matches:
        # if anything other than single letters separated by whitespaces
        # is found, then the operation is unrecognized
        msg = 'unrecognized table symbol(s)'
        return False, msg  
    regex = r'\b[a-zA-Z]\b'
    matches = re.findall(regex, sub_op, re.IGNORECASE)
    tables = matches
    drop_indexes = []
    for table in tables:
        table = table.strip().upper()
        table_index = alphabet.find(table)
        if (table_index >= 0) and (table_index < len_results):
            drop_indexes.append(table_index)
        else:
            print(change_text_color("NON-CRITICAL ERROR: ", 'red', 'keep') + "Table " + bold_text(change_text_color(f"{table}", 'blue', 'keep')) + " not found in results!")
    if drop_indexes != 0:
        for index in range(0,len_results):
            if not (index in drop_indexes):
                output.append(results[index])
        return True, output
    else:
        msg = 'unrecognized table symbol(s)'
        return False, msg

def edit_op(sub_op: str, results: list):
    alphabet = string.ascii_uppercase
    len_results = len(results)
    output = results.copy()
    # find table's cypher
    # there can only be one table per edit operation
    regex = r'^(?:\s*)\b[a-zA-Z]\b'
    matches = re.findall(regex, sub_op, re.IGNORECASE)
    if not bool(re.match(regex, sub_op, re.IGNORECASE)):
        msg = 'unrecognizable table index'
        return False, msg
    # remove table's cypher from sub_op
    sub_op = sub_op[len(matches[0]):]
    table = matches[0].strip().upper()
    table_index = alphabet.find(table)
    # we now have the table index
    # let us get the selected result
    if not (table_index >= 0) and (table_index < len_results):
        msg = f"table '{table}' not found"
        return False, msg
    selected_result = output[table_index]
    # next we need to fetch the table's property that
    # needs to be edited
    # this depends on what type of table it is
    pos = selected_result['pos']
    if pos == 'noun':
        regex = r'^(?:\s*)(text|article|plural|meanings|examples)\b'
    elif pos == 'verb':
        regex = r'^(?:\s*)(text|meanings|ppii|praet|tags|examples)\b'
    elif pos == 'adverb':
        regex = r'^(?:\s*)(text|meanings|examples)\b'
    elif pos == 'adjective':
        regex = r'^(?:\s*)(text|meanings|comparative|superlative|examples)\b'
    # get first word after table's cypher
    # this also checks if property exists in table
    matches = re.findall(regex, sub_op, re.IGNORECASE)
    if not bool(re.match(regex, sub_op, re.IGNORECASE)):
        msg = "unrecognized table property!"
        return False, msg
    selected_property = matches[0].strip().lower()
    sub_op = sub_op[len(matches[0]) + 1:]
    
    # is + or - operation?
    regex = r'^(?:\s*)[+-]'
    matches = re.findall(regex, sub_op, re.IGNORECASE)
    if (len(matches) == 0 or len(matches) > 1):
        msg = 'unrecognized edit operation'
        return False, msg
    operation = matches[0].strip().lower()

    sub_op = sub_op[len(matches[0]):]
    if operation == '+':
        if selected_property in ('meanings', 'examples', 'tags'):
            # check if new values are given as:
            # "value_1", 'value_2', "value_3", etc.
            regex = r'^(?:\s*)(((\"[^\"]*\"))([,]{0,1})(?:\s*))+$'
            if not bool(re.match(regex, sub_op, re.IGNORECASE)):
                msg = "cannot parse argument(s)"
                return False, msg
            regex = r'\"[^\"]*\"'
            # strip all values of quotes and store them in output
            matches = re.findall(regex, sub_op, re.IGNORECASE)
            for match in matches:
                match = match.strip('"').strip()
                if selected_property == 'tags':
                    # in case of verb(s), we need to check new tag(s) integrity
                    # irregular, regular, reflexive, dative, (PPII) mit sein, none

                    #PP2 with sein ==> ^(?:\s*)(p[pz](2|ii)){0,1}(?:\s*)(mit|with|w[\/]{0,1}|\s)(?:\s*)(sein)(?:\s*)$
                    # irregular ==> ^(?:\s*)irre{0,1}(g(u{0,1}l(r\b|ar\b|\b)|\b)|\b)(?:\s*)$
                    # regular ==> ^(?:\s*)regu{0,1}(l(r\b|ar\b|\b)|\b)(?:\s*)$
                    # reflexive ==> ^(?:\s*)ref(l(e{0,1}x(i{0,1}v(e\b|\b)|\b)|\b)|\b)(?:\s*)$
                    # dative ==> ^(?:\s*)dat((i\b|iv\b|v\b|ve\b|ive\b)(?:\s*)$|(?:\s*)$)

                    pp2_regex = r'^(?:\s*)(p[pz](2|ii)){0,1}(?:\s*)(mit|with|w[\/]{0,1}|\s)(?:\s*)(sein)(?:\s*)$'
                    irreg_regex = r'^(?:\s*)irre{0,1}(g(u{0,1}l(r\b|ar\b|\b)|\b)|\b)(?:\s*)$'
                    reg_regex = r'^(?:\s*)regu{0,1}(l(r\b|ar\b|\b)|\b)(?:\s*)$'
                    ref_regex = r'^(?:\s*)ref(l(e{0,1}x(i{0,1}v(e\b|\b)|\b)|\b)|\b)(?:\s*)$'
                    dat_regex = r'^(?:\s*)dat((i\b|iv\b|v\b|ve\b|ive\b)(?:\s*)$|(?:\s*)$)'
                    none_regex = r'^(?:\s*)none(?:\s*)$'
                    if bool(re.match(pp2_regex, match, re.IGNORECASE)):
                        if not ("PPII Mit Sein" in selected_result['tags']):
                            selected_result['tags'].append("PPII Mit Sein")
                    elif bool(re.match(irreg_regex, match, re.IGNORECASE)):
                        if not ("Irregular" in selected_result['tags']):
                            selected_result['tags'].append("Irregular")
                    elif bool(re.match(reg_regex, match, re.IGNORECASE)):
                        if not ("Regular" in selected_result['tags']):
                            selected_result['tags'].append("Regular")
                    elif bool(re.match(ref_regex, match, re.IGNORECASE)):
                        if not ("Reflexive" in selected_result['tags']):
                            selected_result['tags'].append("Reflexive")
                    elif bool(re.match(dat_regex, match, re.IGNORECASE)):
                        if not ("Dative" in selected_result['tags']):
                            selected_result['tags'].append("Dative")
                    elif bool(re.match(none_regex, match, re.IGNORECASE)):
                        if not ("None" in selected_result['tags']):
                            selected_result['tags'].append("None")
                    else:
                        print(change_text_color("NON-CRITICAL ERROR: ", 'red', 'keep') + " Tag " + bold_text(change_text_color(f"{match}", 'blue', 'keep')) + " not acceptable!")
                else:
                    selected_result[selected_property].append(match)
        else:
            regex = r'^(?:\s*)(((\"[^\"]*\"))(?:\s*))+$'
            if not bool(re.match(regex, sub_op, re.IGNORECASE)):
                msg = "cannot parse argument(s)"
                return False, msg
            match = re.search(regex, sub_op, re.IGNORECASE)
            match = match.group(0)
            match = match.strip()
            match = match.strip('"')
            match = match.strip()
            if selected_property == 'article':
                regex = r"^(?:\s*)(das|der|die)(?:\s*)$"
                if bool(re.match(regex, match, re.IGNORECASE)):
                    selected_result[selected_property] = match.title()
                else:
                    regex = r'^(?:\s*)((der(?:\s*)\/(?:\s*)die)|(die(?:\s*)\/(?:\s*)der))(?:\s*)$'
                    if bool(re.match(regex, match)):
                        selected_result[selected_property] = 'Der/Die'
            
            # these properties require all individual words to be capitalized
            elif selected_property == 'text' or selected_property == 'plural' or selected_property == 'comparative' or selected_property == 'superlative':
                selected_result[selected_property] = match.title()
            else:
                selected_result[selected_property] = match
        output[table_index] = selected_result
    else:
        if not isinstance(selected_result[selected_property], list):
            msg = "delete operation can only be performed on list properties"
            return False, msg
        # list of values we want to delete
        pop_list = []
        len_selected_results = len(selected_result[selected_property])
        regex = r"^(?:\s*)all(?:\s*)$"
        if bool(re.match(regex, sub_op, re.IGNORECASE)):
            pop_list = range(0, len_selected_results)
        else:
            regex = r'(?:\s*)\d+(?:\s*)'
            if not bool(re.match(regex, sub_op, re.IGNORECASE)):
                msg = "unrecognized index(es)"
                return False, msg
            matches = re.findall(regex, sub_op, re.IGNORECASE)
            for match in matches:
                match = match.strip()
                match = int(match) - 1
                if not (match in range(0, len_selected_results)):
                    print(change_text_color("NON-CRITICAL ERROR: ", 'red', 'keep') + "Entry " + bold_text(change_text_color(f"{match + 1}", 'blue', 'keep')) + f" not found in {pos}!")
                else:
                    pop_list.append(match)
        non_deleted_vals = []
        for i in range(0, len_selected_results):
            if not (i in pop_list):
                non_deleted_vals.append(selected_result[selected_property][i])
        output[table_index][selected_property] = non_deleted_vals
    return True, output 

# if __name__ == '__main__':
def main():
    cli_args = cli_args_parser()
    
    niveau = cli_args.get('niveau')
    week = cli_args.get('week')
    best_only = cli_args.get('best_only')
    print_errors = cli_args.get('print_errors')

    # validate niveau:
    is_valid = False
    if niveau:
        is_valid = validate_niveau(niveau)
        if not is_valid:
            print(change_text_color('NON-CRITICAL ERROR:', 'red', 'keep') + ' invalid niveau!')
    while not is_valid:
        niveau = input("Vocabase Language Level: ")
        is_valid = validate_niveau(niveau)
        if not is_valid:
            print(change_text_color('NON-CRITICAL ERROR:', 'red', 'keep') + ' invalid niveau!')

    
    # validate week
    is_valid = False
    if week:
        if week.isdecimal():
            week = int(week)
            if week > 0:
                is_valid = True
        if not is_valid:
            print(change_text_color('NON-CRITICAL ERROR:', 'red', 'keep') + ' invalid week!')
    while not is_valid:
        week = input("Vocabase Week DB: ")
        if week.isdecimal():
            week = int(week)
            if week > 0:
                is_valid = True
        if not is_valid:
            print(change_text_color('NON-CRITICAL ERROR:', 'red', 'keep') + 'invalid week!')
    
    # validate fetch_all
    get_first_only = False
    if best_only == None:
        get_first_only = True
    
    # validate print_errors
    suppress_errors = True
    if not print_errors == None:
        suppress_errors = False

    notion = Notion_API_Handler(niveau, week)
    query_again = True
    while query_again:

        print()
        print("Enter" + bold_text(change_text_color(" Any Whitespace Character ", 'blue', 'keep')) + "To Exit Program")
        query = input(change_text_color("Enter A Query:", 'yellow', 'keep') + " ")
        results = []
        if (query != '') and (query.isalpha()):
            query = query.split()[0].strip()
            results = lemmaScraper(query, False, suppress_errors)

            # handle empty results
            if (not isinstance(results, list)) or (len(results) == 0):
                print(change_text_color("Failure!", 'red', 'keep') + " no Lemmas were scraped :(")
                query_again = True
                continue

            prompt_operations(results, notion)
        
        elif query.isspace():
            query_again = False
            break

        else:
            print(change_text_color('INPUT ERROR: ', 'red', 'keep') + "non valid input detected!")
            print('please try again...')
            query_again = True
            continue

        query_again = prompt_yes_no('Query Again (y/n)?')
            


        

    # parse op: [insert, edit, drop, join]
    # based on op -> call: insert_op(), edit_op(), drop_op, join_op()
    # insert_op -> it can either return (True, results), (False, msg)
    # drop_op -> returns either (True, results), (True, None), (False, msg)
            
        
    # don't forget to add join later



# handle multiple return values by utilizing type(return[0])
# return success(bool), clause(str), tables(list), operation(+/-), args(list)
# if tables = [-1] means all



def parse_op2(command: str):
    success = False
    clause = ''
    output_tables = []
    operation = ''
    args = []

    cmd = command

    alphabet = string.ascii_uppercase
    if not isinstance(cmd, str):
        raise TypeError
    
    # tokenize op
    cmd = cmd.lower().split()

    # deal with op one token at a time

    # determine if valid clause or not
    clause = cmd.pop(0)
    
    if not (clause in ("insert","in", 'i', 'edit', 'ed', 'e', 'drop', 'dr', 'd', 'join', 'jn', 'j')):
        msg = "no valid clause detected!"
        return False, msg
    

    # handle insert op
    if clause in ('insert', 'in', 'i'):
        if len(cmd) < 1:
            msg = "no operand(s) detected!"
            return False, msg
        

        if len(cmd) == 1:
            table = cmd[0].upper()
            if table == 'ALL':
                output_tables = [-1]
                return True, clause, output_tables
            else:
                if len(table) == 1:
                    if table.isalpha():
                        output_tables = output_tables.append(alphabet.find(table))
                        return True, clause, output_tables
                    else:
                        msg = f"invalid table index!"
                        return False, msg
                else:
                    msg = f"invalid table index!"
                    return False, msg
        else:
            # handle each table in list
            for table in cmd:
                if (len(table) != 1) or not table.isalpha():
                    msg = 'invalid table index!'
                    return False, msg
                
                table = table.upper()
                table_index = alphabet.find(table)
                output_tables.append(table_index)
            return True, clause, output_tables
    
    # handle drop op
    elif clause in ('drop', 'dr', 'd'):
        if len(cmd) < 1:
            msg = "no operand(s) detected!"
            return False, msg

        if len(cmd) == 1:
            if cmd[0] == 'all':
                return True, clause, [-1]
            elif cmd[0].isalpha() and (len(cmd[0]) == 1):
                output_tables.append(alphabet.find[cmd[0]])
                return True, clause, output_tables
        else:
            for table in cmd:
                if (len(table) != 1) or not table.isalpha():
                    msg = 'invalid table index!'
                    return False, msg
                
                table = table.upper()
                output_tables.append(alphabet.find(table))
            return True, clause, output_tables
          
    elif clause in ('edit', 'ed', 'e'):

        table = cmd.pop(0)

        # after clause type comes only one table letter
        if (len(table) != 1) or not table.isalpha():
            msg = 'non-valid table index!'
            return False, msg
        
        table = table.upper()
        table_index = alphabet.find(table)

        table_property = cmd.pop(0)

        general_properties = ['text', 'meanings', 'examples']
        verb_properties = ['ppii', 'praet', 'tags']
        noun_properties = ['plural', 'article']
        adj_properties = ['comparative', 'superlative']
        combined_properties = general_properties + verb_properties + noun_properties + adj_properties

        if not (table_property in combined_properties):
            msg = f"table property '{table_property}' is not recognized"
            return False, msg
        
        operation = cmd.pop(0)
        
        args = []
        if len(operation) > 1:
            if not (operation[0] in ('+', '-')):
                msg = 'invalid editing operation!'
                return False, msg
            else:
                operation = operation[0]
        elif not operation in ('+', '-'):
            msg = 'invalid editing operation!'
            return False, msg
        
        if operation == '+':
            raw_args = command[command.find('+')+1:]
            regex = r'"[^"]+"'
            args = re.findall(regex, raw_args)
            # args can be multiple matches only if property is a list
            if (table_property in ('meanings', 'examples', 'tags')):
                temp = []
                for arg in args:
                    arg = arg.strip('"')
                    temp.append(arg)
                args = temp
            else:
                if len(args) > 1:
                    msg = f"'{table_property}' only accepts a single value!"
                    return False, msg
                arg = args.pop[0]
                arg = arg.strip('"')
                args.append(arg)
                # True, table_index, table_property, operation, args
        else:
            if not (table_property in ('meanings', 'examples', 'tags')):
                msg = 'delete operation is only valid with list properties!'
            args = command[command.find('-')+1:]
            args = args.split()
            temp = []
            for arg in args:
                if (not arg.isdecimal()):
                    msg = 'invalid editing operation arguments!'
                    return False, None
                else:
                    arg = int(arg)
                    if arg == 0:
                        msg = 'entries have indexes from 1, zero index not accepted!'
                        return False, msg
                    temp.append(arg - 1)
            args = temp
        return True, clause, table_index, table_property, operation, args
    
    # join op
    

        


        


    # insert  <table(s) or all>
    # edit  <table>  <property>  [+ or -]  [(for + -> {new entry}) (for - -> {old entry number(s)})]
    # drop  <table(s) or all>
    # join <table(s) or all>
    # in / ed / dr / jn

    pass

# def join_op(sub_op: str, )
# verb = {'pos': 'verb', 'text': 'Strecken', 'meanings': ['To stretch', 'To elongate', 'To lengthen', 'To eke out'], 'ppii': 'Haben gestreckt', 'praet': 'Streckte', 'tags': ['Regular'], 'examples': ['Ich musste meinen Arm strecken, um das Buch auf dem hohen Regal zu erreichen.']}
# noun = {'pos': 'noun', 'text': 'Strecke', 'article': 'Die', 'plural': 'Strecken', 'meanings': ['Route', 'Line', 'Distance', 'Stretch', 'Course', 'Road'], 'examples': ['Am Ende meiner Straße war eine Absperrung, also musste ich eine andere Strecke fahren. ', 'Ich überhole nur auf einer geraden Strecke.', 'Wir legten die Strecke für unser Autorennen fest.']}
# adverb = {'pos': 'adverb', 'text': 'Heute', 'meanings': ['Today', 'Nowadays', 'This day', 'These days', 'In these days', 'At present'], 'examples': ['Es hat die ganze Woche geregnet, aber heute scheint endlich die Sonne.', 'Ich werde heute ein neues Auto kaufen.', 'Heute findet man wichtige Informationen im Internet.']}
# adjective = {'pos': 'adjective', 'text': 'Seltsam', 'meanings': ['Strange', 'Curious', 'Odd', 'Peculiar', 'Weird', 'Outlandish'], 'comparative': 'Seltsamer', 'superlative': 'Am seltsamsten', 'examples': ['Ich hörte ein seltsames Geräusch und öffnete die Tür.', 'Von der Küche geht ein seltsamer Geruch aus. ', 'Es ist seltsam, dass sie nicht mit uns zum Fest kommen wollte.']}

# results = [verb, noun, adverb, adjective]

# parse_op2('edit c text + "kiwi is better :)" "hello world"')

if __name__=="__main__":
    main()
    pass





