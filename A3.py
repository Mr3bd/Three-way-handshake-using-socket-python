# -------------------------
# Network Programming and Applications
# First Semester (2023-2024)
# Assignment 2
# -------------------------

# -------------------------
# Student Name: Abdullrahman Wasfi
# Student ID  : 20190270f
# -------------------------

# put your import statements between these two lines
# ----------------------------------
from socket import *
from cryptography import *
from utilities import *
from hashlib import *
# ----------------------------------
# I borrowed the A2 solution from myself

BUFFER = 64  # receive buffer for commands
ENCODING = 'utf-8'  # encoding used by both ends
SERVER_ADDRESS = ('localhost', 6330)  # server socket address
BACKLOG = 6  # listen backlog
BLOCK_SIZE = 128  # block size for upload/download
TEXT_EXTENSIONS = ['txt', 'rtf', 'html']  # valid text file extensions
PIC_EXTENSIONS = ['png', 'jpg', 'gif']  # valid picture file extensions


def write(file, msg):
    fh = open(file, 'a')
    fh.write(str(msg))
    fh.close()
    return


'_______________________________________________________________'


# DONE
def prepare_socket(filename, sock_type='client', address=None):
    sock = None

    if sock_type == 'client':
        try:
            sock = socket(AF_INET, SOCK_STREAM)
            write(filename, 'stp(client): socket created\n')

        except Exception as e:
            write(filename, 'stp(client): socket creation failed\n')
            return None

    elif sock_type == 'server':
        try:
            sock = socket(AF_INET, SOCK_STREAM)
            write(filename, 'stp(server): socket created\n')
            try:
                sock.bind(address)
                write(filename, 'stp(server): bound to {}\n'.format(address))
                try:
                    sock.listen(BACKLOG)
                    write(filename, 'stp(server): listening ...\n\n')
                except:
                    write(filename, 'stp(server): listen fatal error\n')
                    return None

            except:
                write(filename, 'stp(server): bind fatal error\n')
                return None
        except:
            write(filename, 'stp(server): socket creation failed\n')
            return None

    return sock

    """
    ----------------------------------------------------
    Parameters:   filename (str)
                  sock_type (str): 'client' or 'server'
                  address (?): None or IPv4 socket address
    Return:       sock (socket)
    Used by:      Client and Server
    Description:  Creates and returns a socket
                  if invalid sock_type:
                      return None
                  if sock_type is client:
                      create socket and return it
                  if sock_type is server:
                      create + bind + listen and return the socket
                  if socket creation is successful:
                      write to file: 'stp(<type>): socket created'
                  otherwise:
                      write to file: 'stp(<type>): socket creation failed
                      return None
                  if bind is successful:
                      write to file: 'stp(server): bound to <address>'
                  otherwise:
                      write to file: 'stp(server): bind fatal error'
                      return None
                  if listen is successful:
                      write to file: 'stp(server): listening ...\n'
                  otherwise:
                      write to file: 'stp(server): listen fatal error'
                      return None                      
    ---------------------------------------------------
    """
    # your code here
    # return 'None'


'_______________________________________________________________'


def stp_server(filename, server_address, client_count):
    """
    ----------------------------------------------------
    Parameters:   filename (str)
                  server_address (tuple): IPv4 socket address
                  client_count (int): number of clients to serve before closing
    Return:       -
    Used by:      Server
    Description:  Main server function.
                  Creates a server socket, 
                  accept clients and direct to handle_client
                      writes to outfile: 'stp(server): accepted client connection <#>'
                  Serves given number of clients then close
    Dependencies: prepare_socket, close_socket, handle_client
    ---------------------------------------------------
    """
    server_socket = prepare_socket(filename, 'server', server_address)
    if server_socket is None:
        return

    for n in range(client_count):
        client_socket, client_address = server_socket.accept()
        write(filename, 'stp(server): accepted client connection #{}\n'.format(n+1))
        handle_client(filename, client_socket)
        close_socket(filename,client_socket, 'server')
        write(filename, '\n')

        
    close_socket(filename,server_socket, 'server')
    return


'_______________________________________________________________'


def handle_client(filename, connection):
    """
    ----------------------------------------------------
    Parameters:   filename (str)
                  connection (socket): client socket accepted by server
    Return:       -
    Used by:      Server
    Description:  Server function to handle clients
                  1- Receives commands from client
                  2- Process commands and send a response
                  3- if valid configuration, download file
                  4- close connection
    Exceptions:   Exception: 'stp(server): handle client error'
    Dependencies: receive_commands, download_file, close_socket
    ---------------------------------------------------
    """
    try:
        response, commands = receive_commands(filename, connection)

        if response == '<config_valid>':

            download_success = download_file(filename, connection, commands)
            if not download_success:
                raise Exception('stp(server): handle client error')
        
    except Exception as e:
        write(filename, f'stp(server): handle client error: {e}\n')

    return


'_______________________________________________________________'


def receive_commands(filename, connection):
    """
    ----------------------------------------------------
    Parameters:   filename (str)
                  connection (socket): client socket accepted by server
    Return:       response (str)
                  commands (list)
    Used by:      Server
    Description:  Receive and process client commands
                  1- Receives commands from client until '<config_done>'
                      write to file: received commands
                  2- Check if given configuration/commands is valid
                      if valid: write to file: configuration
                  3-Send response to client
                      write to file: sent response
                  4- return copy of response and processed commands
    Dependencies: validate_configuration
    ---------------------------------------------------
    """
    try:

        received_commands = ''

        while True:
            data = connection.recv(BUFFER).decode(ENCODING)
            received_commands += data
            if '<config_done>' in received_commands:
                break
        write(filename, 'stp(server): received: {}\n'.format(received_commands))
        string_to_check = received_commands.replace('<config_done>', "")
        tup = validate_configuration(string_to_check)
        res = tup[0]
        # print(res)
        connection.sendall(res.encode(ENCODING))
        write(filename, 'stp(server): sent: {}\n'.format(res))
        res_copy = res
        com_copy = received_commands

        return res_copy, com_copy

    except Exception as e:
        return "Error", []


'_______________________________________________________________'


def validate_configuration(commands):
    if not valid_commands_format(commands):
        return ('#10:BAD_CMD#', [])
    else:
        hasname = False
        hastype = False
        hassize = False
        coms = []
        if type(commands) is list:
            coms = commands
        else:
            coms.append(commands)

        for c in coms:
            if 'name' in c:
                fname = get_parameter_value(coms, 'name')
                hasname = True
            if 'type' in c:
                ftype = get_parameter_value(coms, 'type')
                hastype = True

            if 'size' in c:
                fsize = get_parameter_value(coms, 'size')
                hassize = True
        if hasname and hastype and hassize:
            for c in coms:
                if 'name' in c:
                    if fname is None or not valid_filename(fname):
                        return '#30:BAD_CONFIG#', []

                if 'type' in c:
                    if ftype is None or (ftype != 'text' and ftype != 'pic'):
                        return '#30:BAD_CONFIG#', []
                    else:
                        dot_index = fname.rfind(".")
                        if dot_index != -1:
                            file_extension = fname[dot_index + 1:]

                            if (file_extension not in TEXT_EXTENSIONS) and (file_extension not in PIC_EXTENSIONS):
                                return '#30:BAD_CONFIG#', []
                        else:
                            return '#30:BAD_CONFIG#', []

                if 'size' in c:
                    if fsize is None:
                        return '#30:BAD_CONFIG#', []
                    elif fsize.isdigit():
                        sizevalue = int(fsize)
                        if sizevalue < 1:
                            return '#30:BAD_CONFIG#', []
                    else:
                        return '#30:BAD_CONFIG#', []
            return '<config_valid>', coms
        else:
            return '#20:CMD_MISS#', []

    """
    ----------------------------------------------------
    Parameters:   commands (list or str)
    Return:       response (str) one of the following messages:
                      '#10:BAD_CMD#'
                      '#20:CMD_MISS#'
                      '#30:BAD_CONFIG#'
                      '<config_valid>'
                  commands (list)
    Used by:      Server
    Description:  Check if given commands are valid
                  1- Check if they have proper format
                      if invalid: return '#10:BAD_CMD#' and empty commands list
                  2- Check if it has filename, filetype and filesize
                      if invalid: return '#20:CMD_MISS#' and empty commands list
                  3- Check if filename, filetype and filesize has valid values
                      if invalid: return '#30:BAD_CONFIG#' and empty commands list
                  4- if validated: return '<config_valid>' and commands list
    Dependencies: valid_commands_format, get_parameter_value, valid_filename
    ---------------------------------------------------
    """
    # your code here
    return None


'_______________________________________________________________'


def download_file(out_filename, sock, commands):
    """
    ----------------------------------------------------
    Parameters:   out_filename (str)
                  sock (socket)
                  commands (list)
    Return:       True / False
    Used by:      Server
    Description:  downloads a file from the client using given configuration
                  The file contents are received as text or binary depending on file type
                  In both cases, the function receives BLOCK_SIZE bytes in each receive call
                  If download of "filename.ext" is successful:    
                      Store file as: filename_copy.ext
                      write to file: 'stp(server): download complete'
                      return True
                  If there was an error in download
                      write to file: 'stp(server): receive error: <Exception>'
                      return False   
                  Upon start of download write to file: 'stp(server): downloading ...'
                      write to file every received block
    ---------------------------------------------------
    """
    try:
        f_name = get_parameter_value(commands.replace('<config_done>', ""), 'name')
        dot_index = f_name.find('.')
        write(out_filename, 'stp(server): configuration:\n')
        write(out_filename, 'stp(server): downloading ...\n')
        
        if dot_index != -1:
            file_extension = f_name[dot_index + 1:]
            mode = None
            
            if file_extension in TEXT_EXTENSIONS:
                mode = 'w'
            elif file_extension in PIC_EXTENSIONS:
                mode = 'wb'

            down_file_name = '{}_copy.{}'.format(f_name[:dot_index],file_extension)

            if mode is not None:
                with open(down_file_name, mode) as file:
                    while True:
                        data = sock.recv(BLOCK_SIZE)
                        if not data:
                            break

                        if mode == 'w':
                            file.write(data.decode(ENCODING))
                            if str(data) != "b' '":
                                write(out_filename, 'stp(server): received: {}\n'.format(str(data)))
                        else:
                            trimmed_block = data.rstrip(b' ')
                            file.write(trimmed_block)
                            if str(data) != "b' '":
                                write(out_filename, 'stp(server): received: {}\n'.format(data))
            else:
                write(out_filename, 'stp(server): receive error\n')
                return False

        write(out_filename, 'stp(server): download complete\n')
        return True

    except Exception as e:
        write(out_filename, 'stp(server): receive error: {}\n'.format(e))
        return False


'_______________________________________________________________'


# DONE
def get_file_parameters(filename):
    dot_index = filename.rfind(".")
    # ['$name:sample1.txt$', '$type:text$', '$size:607$']
    list = []
    if dot_index != -1:
        file_extension = filename[dot_index + 1:]
        name = '$name:{}$'.format(filename)
        list.append(name)
        if file_extension.lower() in TEXT_EXTENSIONS:
            type = '$type:text$'
            list.append(type)
            try:
                with open(filename, 'r') as file:
                    content = file.read()
                    total_characters = 0
                    total_characters += len(content)
                    size = '$size:{}$'.format(total_characters)
                    list.append(size)
            except FileNotFoundError:
                pass

        elif file_extension.lower() in PIC_EXTENSIONS:
            type = '$type:pic$'
            list.append(type)
            try:
                with open(filename, 'rb') as file:
                    byte_count = 0
                    while file.read(1):
                        byte_count += 1
                    size = '$size:{}$'.format(byte_count)
                    list.append(size)
            except FileNotFoundError:
                pass
        else:
            try:
                with open(filename, 'rb') as file:
                    file.seek(0, 2)  # Move the file cursor to the end
                    size_bytes = file.tell()
                    size = '$size:{}$'.format(size_bytes)
                    list.append(size)
            except FileNotFoundError:
                pass

    """
    ----------------------------------------------------
    Parameters:   filename(str)
    Return:       parameters (list)
    Used by:      Client
    Description:  Analyzes a given file to get its type and size
                    if invalid filename: return empty list
                    inspect file extension to get its type as defined by
                        TEXT_EXTENSIONS and PIC_EXTENSIONS in utilities
                        if undefined: do not add type parameter
                    compute file size:
                        if file type is text: count number of characters
                        if file type is pic: count number of bytes
                        if file does not exit: do not add size     
    ---------------------------------------------------
    """
    # your code here

    return list


'_______________________________________________________________'


# DONE
def close_socket(filename, sock, sock_type='client'):
    res = False

    if sock.fileno() == -1:
        return False

    if sock_type == 'client':
        try:
            sock.send(b" ")
            try:
                sock.shutdown(SHUT_RDWR)
                write(filename, 'stp(client): connection shutdown\n')
                try:
                    sock.close()
                    write(filename, 'stp(client): socket closed\n')
                    res = True
                except:
                    write(filename, 'stp(client): socket close failed\n')
            except Exception as e:
                write(filename, 'stp(client): shutdown failed\n')
        except:
            try:
                sock.close()
                write(filename, 'stp(client): socket closed\n')
                res = True
            except:
                write(filename, 'stp(client): socket close failed\n\n')
        # res = True

    elif sock_type == 'server':
        try:
            sock.close()
            write(filename, 'stp(server): socket closed\n')
            res = True
        except Exception as e:
            write(filename, 'stp(server): socket close failed\n')

    return res
    """
    ----------------------------------------------------
    Parameters:   filename (str)
                  sock (socket object)
                  sock_type (str): 'client' or 'server'
    Return:       True or False
    Used by:      Client and Server
    Description:  if invalid type: take no action and return False
                  if socket is closed: take no action and return False
                  if listening server socket: close
                  if connected client socket: shutdown then close
                  if disconnected client socket: close
                  when shutdown is successful write to file:
                      'stp(<type>): connection shutdown'
                  otherwise:
                      'stp(<type>): shutdown failed'
                  when close is successful write to outfile:
                      'stp(<type>): socket closed'
                  otherwise:
                      'stp(<type>): socket close failed'
                  if both shutdown/close are successful: return True
                      otherwise: return False
    ---------------------------------------------------
    """
    # your code here
    return None


'_______________________________________________________________'


def valid_commands_format(commands):
    result = False
    if type(commands) is list:
        if len(commands) == 0:
            return False
        else:
            for c in commands:
                dolars = 0
                containSemi = False
                if len(c) < 3:
                    return False

                if c[0] != '$' or c[-1] != '$':
                    return False

                for char in c:
                    if dolars == 2:
                        dolars = 0
                        if char != '$' or not containSemi:
                            return False
                        if containSemi:
                            containSemi = False

                    if char == '$':
                        dolars += 1
                    elif char == ':':
                        containSemi = True
                result = True
    else:
        dolars = 0
        containSemi = False
        if len(commands) < 3:
            return False

        if commands[0] != '$' or commands[-1] != '$':
            return False

        for char in commands:
            if dolars == 2:
                dolars = 0
                if char != '$' or not containSemi:
                    return False
                if containSemi:
                    containSemi = False

            if char == '$':
                dolars += 1
            elif char == ':':
                containSemi = True

        result = True
    """
    ----------------------------------------------------
    Parameters:   commands(str or list)
    Return:       True or False
    Used by:      Client and Server
    Description:  Inspects given commands and check if its format is valid
                  valid commands:
                      1- contain at least one command
                      2- every command is formatted as: $<command>$
    ---------------------------------------------------
    """
    # your code here
    return result


'_______________________________________________________________'


def get_parameter_value(commands, parameter):
    """
    ----------------------------------------------------
    Parameters:   commands (str or list)
                  parameter (str)
    Return:       value (str)
    Used by:      Client and Server
    Description:  Returns the value of the given parameter in commands
                    if commands are not in valid format: return None
                    if parameter undefined: return None
                    Otherwise, return value in string format
    Dependencies:  valid_commands_format
    ---------------------------------------------------
    """
    if valid_commands_format(commands):
        if type(commands) is list:
            for c in commands:
                if parameter in c:
                    start_index = c.find('{}'.format(parameter))
                    val = c[start_index:]
                    semi_index = val.find(":")
                    dollar_index = val.find("$")
                    if semi_index == -1 or dollar_index == -1:
                        return None
                    else:
                        val = val[semi_index + 1:dollar_index]

                    return val
        else:
            start_index = commands.find('{}'.format(parameter))
            val = commands[start_index:]
            semi_index = val.find(":")
            dollar_index = val.find("$")
            if semi_index == -1 or dollar_index == -1:
                return None
            else:
                val = val[semi_index + 1:dollar_index]

            return val

    return None


'_______________________________________________________________'


def stp_client(out_filename, server, filename=None, commands=None, i=None):
    """
    ----------------------------------------------------
    Parameters:   out_filename (str)
                  server_address (tuple): IPv4 socket address
                  filename (str or None): filename to be uploaded
                  commands (list or None): file transfer commands
    Return:       -
    Used by:      Client
    Description:  Main client function, performs the following
                  1- Creates a client socket
                  2- Connect to server
                  3- if commands is None extract file configuration
                  4- Send commands to server
                  5- Receive response from server
                  6- If configuration is approved by server: upload file
                  7- close the connection and socket
    Dependencies: prepare_socket, close_socket, connect_to_server, 
                    get_file_parameters, send_commands, get_config_response,
                    upload_file
    Errors:        The function returns in the following cases:
                        filename and commands are None
                        Creating the socket failed
                        Connecting to server failed
    Exception:    write to file: 'stp(client): Exception: <Exception>'
    ---------------------------------------------------
    """
    try:
        client_sock = prepare_socket(out_filename, 'client')
        try:
            connect_to_server(out_filename, client_sock, server)
            if commands is None:
                commands = get_file_parameters(filename)
            if len(commands) > 0:
                result = send_commands(out_filename, client_sock, commands)
                if result:
                    response = get_config_response(out_filename, client_sock)
                    if 'config_valid' in response:
                        upload_res = upload_file(out_filename, client_sock, commands)


        except Exception as e:
            write(out_filename, 'stp(client): Exception: {}'.format(e))
            close_socket(out_filename, client_sock, 'client')
        finally:
            close_socket(out_filename, client_sock, 'client')
    except Exception as e:
        write(out_filename, 'stp(client): Exception: {}'.format(e))


'____________________________________________________'


def connect_to_server(filename, sock, server, ):
    """
    ----------------------------------------------------
    Parameters:   filename (str)
                  sock (socket)
                  server (tuple): server address
    Return:       True / False
    Used by:      Client
    Description:  connects given socket to the given address
                  if successful: return True
                  if connect fails: 
                      close socket
                      write to file: stp(client): connect fatal error
                      return False
    Dependencies: close_socket
    ---------------------------------------------------
    """
    try:
        sock.connect(server)
        return True

    except:
        write(filename, 'stp(client): connect fatal error\n')
        close_socket(filename, sock, 'client')
        return False


'____________________________________________________'


def send_commands(filename, sock, commands):
    """
    ----------------------------------------------------
    Parameters:   filename (str)
                  sock (socket)
                  commands (list)
    Return:       True / False
    Used by:      Client
    Description:  send given commands to server
                  each command is sent using a separate send operation
                  write to file each sent command
                  When done send: '<config_done>' and return True
                  if sending fails: 
                      write to file: 'stp(client): send operation failed'
                      return False
    ---------------------------------------------------
    """
    try:

        for command in commands:
            sock.sendall(command.encode(ENCODING))
            write(filename, 'stp(client): sent: {}\n'.format(command))
        # print('client sent all commands')
        completion_command = '<config_done>'
        sock.sendall(completion_command.encode(ENCODING))
        write(filename, 'stp(client): sent: {}\n'.format(completion_command))

        return True

    except:
        write(filename, 'stp(client): send operation failed')
        return False


'____________________________________________________'


def get_config_response(filename, sock):
    """
    ----------------------------------------------------
    Parameters:   filename (str)
                  sock (socket)
    Return:       response (str)
    Used by:      Client
    Description:  receives the server response to the sent commands
                  if successful: 
                      write to file: 'stp(client): received: <msg>'
                      return response message
                  if failed: write to outfile:
                      write to file: 'stp(client): configuration receive error: <Exception>'
                      return empty string
    ---------------------------------------------------
    """
    try:
        # print('wait to get response from server')
        response = sock.recv(BUFFER).decode(ENCODING)
        # print('received response from server: {}'.format(response))
        write(filename, 'stp(client): received: {}\n'.format(response))
        return response

    except Exception as e:
        write(filename, f'stp(client): configuration receive error: {e}\n')
        # ('response from server is empty')
        return ''


'____________________________________________________'


def upload_file(out_filename, sock, commands):
    """
    ----------------------------------------------------
    Parameters:   out_filename (str)
                  sock (socket)
                  commands (list)
    Return:       True/False
    Used by:      Client
    Description:  uploads given file to the server
                  Send file as text or binary for pictures
                  file is sent in blocks of size BLOCK_SIZE
                  write to file: 'stp(client): uploading ...'
                  write to file blocks as: 'stp(client): sent: <block>'
                  write to file: 'stp(client): uploading complete'
    Errors:       if commands are not in valid format: return False
                  if opening file fails: write 'stp(client): uploading failed\n', return False
                  other errors: 'stp(client): uploading failed: <Exception>', return False
    ---------------------------------------------------
    """

    f_name = get_parameter_value(commands, 'name')

    try:
        write(out_filename, 'stp(client): uploading ...\n')
        dot_index = f_name.rfind(".")
        if dot_index != -1:
            file_extension = f_name[dot_index + 1:]
            mode = None
            
            if file_extension in TEXT_EXTENSIONS:
                mode = 'r'
            elif file_extension in PIC_EXTENSIONS:
                mode = 'rb'
            
            if mode is not None:
                with open(f_name, mode) as file:
                    while True:
                        block = file.read(BLOCK_SIZE)

                        if not block:
                            break
                        if mode == 'r':
                            if str(block.encode(ENCODING)) != "b' '":
                                sock.sendall(block.encode(ENCODING))
                                write(out_filename, 'stp(client): sent: {}\n'.format(str(block.encode(ENCODING))))

                        else:
                            if block != "b' '":
                                trimmed_block = block.rstrip(b' ')
                                sock.sendall(trimmed_block)
                                write(out_filename, 'stp(client): sent: {}\n'.format(str(trimmed_block)))


            else:
                write(out_filename, 'stp(client): uploading failed\n')
                return False

        write(out_filename, 'stp(client): uploading complete\n')
        return True

    except FileNotFoundError:
        write(out_filename, 'stp(client): uploading failed\n')
        return False

    except Exception as e:
        write(out_filename, 'stp(client): uploading failed: {}\n'.format(e))
        return False


'____________________________________________________'


def valid_filename(filename):
    """
    ----------------------------------------------------
    Parameters:   filename (str)
    Return:       True/False
    Description:  Checks if given input is a valid filename 
                  a filename should have at least 3 characters
                  and contains a single dot that is not the first or last character
    ---------------------------------------------------
    """
    if type(filename) != str:
        return False
    if len(filename) < 3:
        return False
    if '.' not in filename:
        return False
    if filename[0] == '.' or filename[-1] == '.':
        return False
    if filename.count('.') != 1:
        return False
    return True
