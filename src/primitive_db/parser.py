def parse_where(args):
    if len(args) != 3 or args[1] != "=":
        return None
    
    col = args[0]
    val_str = args[2]

    if val_str.lower() == "true":
        val = True
    elif val_str.lower() == "false":
        val = False
    else:
        try:
            val = int(val_str)
        except ValueError:
            val = val_str
            
    return {col: val}


def parse_set(args):
    if len(args) % 3 != 0 or not args:
        return None
        
    set_dict = {}
    for i in range(0, len(args), 3):
        if args[i+1] != "=":
            return None
        col = args[i]
        val_str = args[i+2]
        
        if val_str.lower() == "true":
            val = True
        elif val_str.lower() == "false":
            val = False
        else:
            try:
                val = int(val_str)
            except ValueError:
                val = val_str
                
        set_dict[col] = val
        
    return set_dict