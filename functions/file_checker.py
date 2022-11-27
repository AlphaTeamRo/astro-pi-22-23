import os

def files_check(logger, base_folder):
    #check if all the files are present
    if os.path.exists(f"{base_folder}/raw"):
        pass
    else:
        try:
            os.makedirs(f"{base_folder}/raw")
            logger.error("There was no raw image directory, so I made one")
        except:
            logger.error("There was no raw image directory and I couldn\'t make one")
    
    if os.path.exists(f"{base_folder}/events.log"):
        pass
    else:
        try:
            logger.error("There was no events.log file, so I made one")
            open(f"{base_folder}/events.log", 'a').close()
        except:
            logger.error("There was no events.log file and I couldn\'t make one")
    
    if os.path.exists(f"{base_folder}/data.csv"):
        pass
    else:
        try:
            logger.error("There was no data.csv file, so I made one")
            open(f"{base_folder}/data.csv", 'a').close()
        except:
            logger.error("There was no data.csv file and I couldn\'t make one")