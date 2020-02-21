import os

file_lock_wait_sc = 5

def is_locked(filepath):
    """Checks if a file is locked by opening it in append mode.
    If no exception thrown, then the file is not locked.
    """
    locked = None
    file_object = None
    if os.path.exists(filepath):
        try:
            #print("Trying to open %s." % filepath)
            buffer_size = 8
            # Opening file in append mode and read the first 8 characters.
            file_object = open(filepath, 'a', buffer_size)
            if file_object:
                #print("%s is not locked." % filepath)
                locked = False
        except IOError:
            print("File is locked.")
            locked = True
        finally:
            if file_object:
                file_object.close()
                #print("%s closed." % filepath)
    else:
        print("%s not found." % filepath)
    return locked