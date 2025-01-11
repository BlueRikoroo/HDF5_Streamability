import threading
import traceback

import h5py
import numpy as np
import time
import os

curLetterID = "A"
def getUniqueID():
    global curLetterID
    returnID = curLetterID
    if curLetterID == "Z":
        curLetterID = "A"
    else:
        curLetterID = chr(ord(curLetterID) + 1)
    return returnID

def standard_write(grow_axis_length, axis_2_length, axis_3_length):
    letterID = f"({getUniqueID()}) "
    print(f"{letterID}Creating File ")
    f = h5py.File("test.h5", "w")
    f.close()
    time.sleep(1)
    print(f"{letterID}Writing {grow_axis_length}x{axis_2_length}x{axis_3_length}")
    array = np.random.rand(grow_axis_length, axis_2_length, axis_3_length)
    f = h5py.File("test.h5", "r+")
    f.create_dataset("data", data=array)
    f.close()

def standard_read():
    letterID = f"({getUniqueID()}) "
    print(f"{letterID}Reading")
    f = h5py.File("test.h5", "r")
    data = f["data"][:]
    f.close()
    print(f"{letterID}Data Loaded with shape ${data.shape}")

def slow_write(grow_axis_length, axis_2_length, axis_3_length):
    letterID = f"({getUniqueID()}) "
    print(f"{letterID}Creating File ")
    f = h5py.File("test.h5", "w")
    f.close()
    time.sleep(1)
    print(f"{letterID}Writing Autox{axis_2_length}x{axis_3_length}")
    f = h5py.File("test.h5", "r+")
    f.create_dataset("data", shape=(0, axis_2_length, axis_3_length), maxshape=(None, axis_2_length, axis_3_length))
    f.close()
    time.sleep(1)
    print(f"{letterID}Starting Writing {grow_axis_length}x{axis_2_length}x{axis_3_length}")
    f = h5py.File("test.h5", "r+")
    for i in range(grow_axis_length):
        print(f"{letterID}Writing grow index {i+1}")
        newData = np.random.rand(axis_2_length, axis_3_length)
        f["data"].resize((i+1, axis_2_length, axis_3_length))
        f["data"][i] = newData
        time.sleep(0.1)
    f.close()


def file_is_stable():
    print("Checking if file is okay")
    problems = 0
    try:
        f = h5py.File("test.h5", "r")
        f.close()
        print("(Good) File Operable")
    except:
        print("(Bad) File Failed to open")
        problems += 1
    try:
        f = h5py.File("test.h5", "r")
        d = f["data"][:]
        f.close()
        print("(Good) Data Loaded")
    except:
        print("(Bad) Data failed to read")
        problems += 1

    return problems == 0

def clear():
    os.remove("test.h5")
    print("File removed, ready for next test")

def test1():
    print("Test 1: Can an HDF5 file be read while it is being created")

    def test_write():
        try:
            standard_write(1000, 1000, 100)
        except:
            print("(Bad) Write failed?")
    def test_read():
        try:
            standard_read()
        except:
            print("(Bad) Unable to read from data when the dataset does not exist yet")
    thread1 = threading.Thread(target=test_write)
    thread2 = threading.Thread(target=test_read)

    print("Starting the write")
    thread1.start()
    time.sleep(1)
    print("Starting the read while thread1 is going")
    thread2.start()

    thread1.join()
    thread2.join()

    print("Done.")
    time.sleep(0.5)
    result = file_is_stable()
    time.sleep(0.5)
    clear()
    return result

def test2():
    print("Test 2. While file is open, slowly write data, then close. Try reading during this process")

    def test_write():
        try:
            slow_write(50, 1000, 1000)
        except:
            print("(Bad) Write failed?")
            traceback.print_exc()
            return False
    def test_read():
        try:
            standard_read()
        except:
            print("(Bad) Unable to read from data when the dataset does not exist yet")

    thread1 = threading.Thread(target=test_write)
    thread2 = threading.Thread(target=test_read)

    print("Starting the write")
    thread1.start()
    time.sleep(5)
    print("Starting the read while thread1 is going")
    thread2.start()

    thread1.join()
    thread2.join()

    print("Done.")
    time.sleep(0.5)
    result = file_is_stable()
    time.sleep(0.5)
    clear()
    return result

def performTest(func):
    try:
        func()
        input("(Enter to continue)")
        os.system('cls' if os.name == 'nt' else 'clear')
    except:
        traceback.print_exc()
        return False
    return True

if __name__ == "__main__":
    performTest(test1)
    performTest(test2)