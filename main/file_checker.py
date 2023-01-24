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
    
    #check if auto-classify exists
    if os.path.exists(f"{base_folder}/auto-classify"):
        #check if subfolders exist
        subfolders = ["day", "night", "twilight"]
        for i in subfolders:
            if os.path.exists(f"{base_folder}/auto-classify/{i}"):
                pass
            else:
                os.makedirs(f"{base_folder}/auto-classify/{i}")
                try:
                    logger.error(f"There was no auto-classify/{i} dir, so I made one")
                except:
                    logger.error(f"There was no auto-classify/{i} dir and I couldn\'t make one")
    else:
        try:
            logger.error("There was no auto-classify dir, so I made one")
            os.makedirs(f"{base_folder}/auto-classify")
        except:
            logger.error("There was no auto-classify dir and I couldn\'t make one")