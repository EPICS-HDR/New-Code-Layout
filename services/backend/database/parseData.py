def ParseData(List):
   
    # Initializes Count Value
    index = 0

    # Iterates through entire length of inputted list
    for item in range(0, len(List)):
        
        # Reinitializes neg check
        neg = 0
        
        # Inititalizes all data to string for parsing
        List[index] = str(List[index])
        
        # Checks if Value is Only a hyphen
        if List[index] == "-":
            List[index] = '0'

        # Checks for Common Error Character (Can add more as issues arise)
        if '"' in List[index]:
            temp = List[index].split('"')

            # Plugs partially parsed data back into list
            List[index] = "".join(temp)

        # Checks for Commas, Removing if Needed
        if "," in List[index]:
            tempList = List[index].split(",")
            Ndata = (tempList[0] + tempList[1])
            
            # Plugs partially parsed data back into list
            List[index] = Ndata

        # Checks if Negative, Makes note
        if "-" in List[index]:
            neg = 1

        # Sets variable for Try test. Removes Issue Characters
        data = List[index].strip('-"')

        # Attempts to make the data a float, assigns value of 0 if not possible
        try:
            data = float(data)
        except:
            data = 0

        # Reapplies negative if needed
        if neg == 1:
            data *= -1

        # Replaces original value with parsed, numerical data
        List[index] = data
        index += 1

    # Returns altered list
    return List