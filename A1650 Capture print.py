
import serial
import time
import os
import keyboard
import shutil
import datetime
import subprocess
import sys

def flush_LA_output_buffer():
    #Open and close selected port while input buffer is empty (flush data in LA output buffer)
    print("Flushing logic analyzer output buffer")
    portOpen = ser.isOpen() #memorize current state
    if portOpen:
        ser.close()
        time.sleep(0.5)
        ser.open()
        time.sleep(0.5)
    else:   
        ser.open()   #open port if is not alredy open
        time.sleep(0.5)
    
    if ser.in_waiting > 0:
        while 1:
            ser.read(ser.in_waiting)
            ser.close()
            ser.open()
            time.sleep(0.5)
            if ser.in_waiting == 0:
                break
    else:
        print("logic analyzer output buffer is empty.")
        
    if not portOpen:
        ser.close() #restore prevoius state

def clearBuffers():
    #FLUSH PC AND LA BUFFERS
    print("Clearing buffers")
    flush_LA_output_buffer()
    ser.reset_input_buffer()
    ser.reset_output_buffer()

def flush_input():
    try:
        import msvcrt
        while msvcrt.kbhit():
            msvcrt.getch()
    except ImportError:
        import sys, termios    #for linux/unix
        termios.tcflush(sys.stdin, termios.TCIOFLUSH)

def main():
    
    print("Print data import from logic analyzer program started")
    
    global ser
    
    ser = serial.Serial(
        'COM6',
        19200, 
        xonxoff = False,  # WARNING: Using this causes PCL file corruption 
                          #          when using Print All on analyzer.
        rtscts = False, 
        bytesize=serial.EIGHTBITS, 
        parity=serial.PARITY_NONE, 
        stopbits=serial.STOPBITS_ONE, 
        timeout=2)

    # Try and spool out any data left in the analyzer serial output buffer
    # or in the local serial buffers.
    # In our specific case this is data incomming from a not yet 
    # timed out print screen that has not been read to completion.
    clearBuffers()

    pcl_file_path = 'print_screen.pcl'
    pdf_file_path = 'print_screen.pdf'

    while True:

        if os.path.exists(pcl_file_path):
            print("Removing old pcl file '" + pcl_file_path + "'")
            os.remove(pcl_file_path)    

        if os.path.exists(pdf_file_path):
            print("Removing old pdf file '" + pdf_file_path + "'")
            os.remove(pdf_file_path)    

        print("Creating new pcl file '" + pcl_file_path + "'...")

        print("Hold down the ENTER key when the logic analyzer has completed printing")

        with open(pcl_file_path, 'wb') as f:
            # Read data from the serial port and write it to the file
            while True:

                # Check if the Enter key is pressed
                if keyboard.is_pressed('enter'):
                    break 
            
                data = ser.read()
                f.write(data)
                f.flush()

        f.close() 

        print("Creating pdf file '" + pdf_file_path + "'")

        # Execute PCL conversion to PDF
        result = subprocess.run(['WinPCLtoPDF.exe', pcl_file_path, pdf_file_path, "/silent"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Get the current date and time
        now = datetime.datetime.now()

        # Format the date and time string
        date_time_string = now.strftime("%Y-%m-%d_%H-%M-%S")

        # Use the date and time string in a file name
        pdf_file_path_final = f"HP1650A Print screen {date_time_string}.pdf"

        shutil.copy(pdf_file_path, pdf_file_path_final)

        print("Created pdf file '" + pdf_file_path_final + "'")
        
        # Prompt the user for a yes/no answer
        answer = ""

        flush_input()

        while True:
            answer = input("Do you want to continue? (yes/no): ")

            # Convert the answer to lowercase
            answer = answer.lower()
            
            if (answer == "yes") or (answer == "y") or (answer == "no") or (answer == "n"):  
                 break

        # Check if the answer is "yes"
        if (answer == "yes") or (answer == "y"):
            print("Continuing...")
    
        # Check if the answer is "no"
        elif (answer == "no") or (answer == "n"):
            print("Exiting...")
            break

        time.sleep(2)
        
        flush_input()

    
if __name__ == "__main__":
    main()