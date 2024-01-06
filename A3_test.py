from A3 import stp_client, stp_server,SERVER_ADDRESS
from threading import Thread
from utilities import write

passwords = ['ZluVHtb5xho27YR','T4QvgRb0tnO8Kiz','XRJ97lKm5GnKIaD',
             'YnM6W2STH8JuFs2','GcD3VxLSBF9ZRNR','eYeix4YwJPToq6T',
             'zMLcq48osQL9Skb','r0Q3IxcDOx3dY8V','8y7Ce4Qpb5HqB5p',
             'Rbq3ICEOs70q4OJ','Sz7BWFxWrZBoXhN','Ns2YoxVmy0qa6gB',
             'bK8WBJYByvQuC9A','mL3y6B8PgoKsuda','zM6gq8u8rjVDWqH',
             'wwgrRewGGoje45O','3qVkDkMC4hLbj3r','BrXLdaxrPW3a1oB',
             'dRARVeEC7qU7Q6N','6ZXW664i2cRgTTW']

symm_keys = [b'FNbuSJ30yFe7YuV0xw9CNH7gKkXNrYBtWToKF8gSY6E=', 
             b'Tlt3p9fwDt90JOPsze8IASb49iJxAn7EFqbsfjMMC1c=', 
             b'tVMIOt5h-ArjEnUMhdUQ4TjXGKYc-p5S7HKzNGkfkQo=', 
             b'qUjuP_758hFzJzkP0CnqTegzQgvji5uDhQOvKEyBxn4=', 
             b'aV33G_gIYyLHWR9QjVUE8QtfQbyfgXobzgEh2qweNig=', 
             b'cVcmHI2UuACN49b_UyKi0TCnWD9-RwCl7AVHlY2peDs=', 
             b'Jwk8eYaTlI8KGwb2liOlOzmbe3MvVoGBoiL8yZ0Zt1o=', 
             b'9Dz89jHQobGt4A-WMQBvk8_qpqgNGUOFRIbvmO4v0B8=', 
             b'6A41_O10G8fAMZmpifv6KpnpLXNPfyG4RFsXJG4qaos=', 
             b'6Rqc1cO5ZDMXrDSAnVK6RPbsZbIyWlsmA-5Ln2cOMO8=', 
             b'iChxcGOEK9b884z84YQBnMbjBBK8GgjpJD2lJMHDYKQ=', 
             b'8GlzEqpw2KYArsouWFxqYV2TiKj05m_mwvsrLRzaeYU=', 
             b'WnWjz7j1UmcisuGxp7yO_88sX3pz-5rD27HbIWXiijM=', 
             b'SRY2cRS6E7i8XX4LlJOEKjjbamYLi1kH9nJHcrVEzcY=', 
             b'Jndz-8AlunRLJI5mk9JKU_EM5Vmsa8wqaCNTAu53vQ8=', 
             b'MzXpABIOgv2OPj8Mb_1wTY-FvaN_7hSadpfzHxqiPyI=', 
             b'vB4whHblZFtV41N1VM1isv4gKDGEaww9ebuPgeRsgJo=', 
             b'rl2n95yE3vox144R6I0BB2Ue9DTeLq1UmSV2z5YvtgQ=', 
             b'sm0929F-YQK-iW7CIIyk7EhIUu5ke9rgeqz3wDls2Xc=', 
             b'LcarbnrqmKdf33YHPbokG5DpHcJCeDrrIDW0Txep8o4=']

def wipe_files(filelist):
    """
    ----------------------------------------------------
    Parameters:   filelist (list)
    Return:       -
    Description:  clear the contents of all given files
    Errors:       If operation fails, an exception is raised
    ---------------------------------------------------
    """
    try:
        for file in filelist:
            outfile = open(file,'w')
            outfile.close()
    except Exception as e1:
        print('clear_files(Exception): {}'.format(e1))
    return

# Test invalid login
def task1():

    server_file = 'A3_student_server.txt'
    write(server_file,"-" * 40)
    write(server_file,"\nStart of task1 Testing\n\n")
    server_thread = Thread(target=stp_server,args=(server_file,SERVER_ADDRESS,2))
    server_thread.start()
    
    client_file = 'A3_student_client.txt'
    write(client_file,"-" * 40)
    write(client_file,"\nStart of task1 Testing\n\n")
    
    passwords = ['MluVHtb5shoy7YN','ZluUHtb7xmoy7YR']
    for i in range(len(passwords)):
        key = (passwords[i],symm_keys[i])
        stp_client(client_file,SERVER_ADDRESS,key,None,[])
        write(client_file,'\n')
        
    write(client_file,'End of task1 Testing\n')
    write(client_file,"-" * 40)
    write(client_file,'\n')

    write(server_file,'\nEnd of task1 Testing\n')
    write(server_file,"-" * 40)
    write(server_file,'\n')
    server_thread.join()

    return

# Test valid login + bad commands
def task2():

    server_file = 'A3_student_server.txt'
    write(server_file,"-" * 40)
    write(server_file,"\nStart of task2 Testing\n\n")
    server_thread = Thread(target=stp_server,args=(server_file,SERVER_ADDRESS,4))
    server_thread.start()
    
    client_file = 'A3_student_client.txt'
    write(client_file,"-" * 40)
    write(client_file,"\nStart of task2 Testing\n\n")
    
    passwords = ['ZluVHtb5xho27YR','YnM6W2STH8JuFs2',
                 'GcD3VxLSBF9ZRNR','eYeix4YwJPToq6T']
    commands = [['tricky!'],
                ['$type:pic$','(size:6501)','$name:t2.txt$'],
                ['$size:-4$','$name:f2.pdf$','$type:text$'],
                ['$size:441$','$type:text$']]
    for i in range(len(passwords)):
        key = (passwords[i],symm_keys[i])
        stp_client(client_file,SERVER_ADDRESS,key,None,commands[i])
        write(client_file,'\n')
        
    write(client_file,'End of task2 Testing\n')
    write(client_file,"-" * 40)
    write(client_file,'\n')

    write(server_file,'\nEnd of task2 Testing\n')
    write(server_file,"-" * 40)
    write(server_file,'\n')
    server_thread.join()

    return

# valid download
def task3():

    server_file = 'A3_student_server.txt'
    write(server_file,"-" * 40)
    write(server_file,"\nStart of task3 Testing\n\n")
    server_thread = Thread(target=stp_server,args=(server_file,SERVER_ADDRESS,1))
    server_thread.start()
    
    client_file = 'A3_student_client.txt'
    write(client_file,"-" * 40)
    write(client_file,"\nStart of task3 Testing\n\n")
    
    passwords = ['GcD3VxLSBF9ZRNR']
    commands = [['$type:text$','$size:607$','$name:t1.txt$']]
    for i in range(len(passwords)):
        key = (passwords[i],symm_keys[i])
        stp_client(client_file,SERVER_ADDRESS,key,None,commands[i])
        write(client_file,'\n')
        
    write(client_file,'End of task3 Testing\n')
    write(client_file,"-" * 40)
    write(client_file,'\n')
    
    server_thread.join()
    write(server_file,'\nEnd of task3 Testing\n')
    write(server_file,"-" * 40)
    write(server_file,'\n')
    server_thread.join()

    return

def main():
    print('Starting Testing')
    
    files = ['A3_student_basic.txt','A3_student_client.txt',
             'A3_student_server.txt','sample1_copy.txt']
    wipe_files(files)

    try:
        print('Task 1 Testing started')
        task1()
        print('Task 1 Testing ended')
    except Exception as e1:
        print('Unhandled exception in task1: {}'.format(e1))
    
    # try:
    #     print('Task 2 Testing started')
    #     task2()
    #     print('Task 2 Testing ended')
    # except Exception as e2:
    #     print('Unhandled exception in task2: {}'.format(e2))
    
    # try:
    #     print('Task 3 Testing started')     
    #     task3()
    #     print('Task 3 Testing Complete')
    # except Exception as e3:
    #     print('Unhandled exception in task3: {}'.format(e3))
                          
    return

main()