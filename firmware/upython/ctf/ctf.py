import machine
import zlib

# from machine import Pin, I2C, Timer


MINI_GIGA_HEAP = [0]*255
heap_list = []
times_freed = 0
CRYPTO_INIT = 0

TYPE_FREE = 0x11
TYPE_INFO = 0x12
TYPE_SECR = 0x13

HANDLE_TO_SECRET = -1

 
allowed = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.:"
def onlyAllowedChar(data):
    for c in data:
        if c not in allowed:
            return False
    return True


def crc16(data, poly = 0xA001):
    '''
        CRC-16 MODBUS HASHING ALGORITHM
    '''
    crc = 0xFFFF
    for byte in data:
        crc ^= ord(byte)
        for _ in range(8):
            crc = ((crc >> 1) ^ poly
                   if (crc & 0x0001)
                   else crc >> 1)

    return (crc // 256, crc & 0xFF) 


def init_heap():
    global heap_list, MINI_GIGA_HEAP, times_freed
    times_freed = 0
    heap_list = [0]
    MINI_GIGA_HEAP = [0]*255
    MINI_GIGA_HEAP[0] = TYPE_FREE
    MINI_GIGA_HEAP[1] = 253

def alloc(len_req, type_req):
    global heap_list, MINI_GIGA_HEAP
    for i in range(len(heap_list)):
        
        if MINI_GIGA_HEAP[heap_list[i]] == TYPE_FREE and MINI_GIGA_HEAP[heap_list[i] + 1] >= len_req:
            prev_free_len = MINI_GIGA_HEAP[heap_list[i] + 1]
            
            # do not reuse crypto object for info to avoid heap fragmentation
            if prev_free_len == 19: 
                continue 
            
            MINI_GIGA_HEAP[heap_list[i]] = type_req
            #chunk is big enough to split
            if MINI_GIGA_HEAP[heap_list[i] + 1] > len_req+2:
                MINI_GIGA_HEAP[heap_list[i] + 1] = len_req
                heap_list.append(heap_list[i] + 2 + len_req)
                
                # create new free chunk
                MINI_GIGA_HEAP[heap_list[i] + 2 + len_req] = TYPE_FREE
                MINI_GIGA_HEAP[heap_list[i] + 2 + len_req + 1] = prev_free_len - 2 - len_req
            return heap_list[i]
    return -1 # no more memory
    
    
def free(ind):
    global heap_list, MINI_GIGA_HEAP
    global times_freed
    times_freed += 1
    if ind in heap_list and (MINI_GIGA_HEAP[ind] == TYPE_INFO or MINI_GIGA_HEAP[ind] == TYPE_SECR):
        #valid object, mark as freed
        print("Freed object ", ind)
        MINI_GIGA_HEAP[ind] = TYPE_FREE
    
    # merge free chunks every once in a while
    if (times_freed == 3):
        times_freed = 0
        merged = True
        while merged:
            merged = False
            for i in range(len(heap_list)-2,-1, -1):
                #print(range(len(heap_list)-1))
                #print("Heap element ", heap_list[i])
                if MINI_GIGA_HEAP[heap_list[i]] == TYPE_FREE:
                    if MINI_GIGA_HEAP[heap_list[i+1]] == TYPE_FREE:
                        #  two concequent chunks are freed, can merge them togeather
                        MINI_GIGA_HEAP[heap_list[i]+1] += 2 + MINI_GIGA_HEAP[heap_list[i+1]+1]
                        MINI_GIGA_HEAP[heap_list[i+1]] = 0x00 # clear the type just in case 
                        print(heap_list)
                        del heap_list[i+1]
                        print(heap_list)
                        merged = True
                        break
            
    

secret = b'x\x9cK\xcbIL\xafvsus\x8d\x0f\x8b\x87P\xb5\x00B\xdb\x06\x88'

def init_crypto():
    global CRYPTO_INIT, HANDLE_TO_SECRET, MINI_GIGA_HEAP
    if CRYPTO_INIT == 0:
        tmp = zlib.decompress(secret).decode()
        ptr = alloc(len(tmp), TYPE_SECR)
        HANDLE_TO_SECRET = ptr
        p = ptr+2
        for c in tmp:
            MINI_GIGA_HEAP[p] = ord(c)
            p += 1 
        CRYPTO_INIT = 1
    else:
        print("Already initialized")
    
def crypto_terminate():
    global CRYPTO_INIT, HANDLE_TO_SECRET
    if CRYPTO_INIT == 1:
        free(HANDLE_TO_SECRET)
        CRYPTO_INIT = 0  



def read_info(ind):
    if (ind in heap_list):
        if (MINI_GIGA_HEAP[ind] == TYPE_INFO):
            print("".join([chr(x) for x in MINI_GIGA_HEAP[ind+2:ind+2+MINI_GIGA_HEAP[ind+1]]]))
        else:
            print("Not a valid INFO heap object\n")
            
def remove_info(ind):
    if (ind in heap_list):
        if (MINI_GIGA_HEAP[ind] == TYPE_INFO):
            free(ind)
        else:
            print("Not a valid INFO heap object\n")

def store_info(data):
    if len(data) > 8:
        print("Info is too long")
        return
    if not onlyAllowedChar(data):
        print("Illegal character")
        return
        
    ptr = alloc(8, TYPE_INFO) # TODO maybe remove magic numbers and robust CI/CD security testing
    #MINI_GIGA_HEAP[ptr] = TYPE_INFO
    #MINI_GIGA_HEAP[ptr+1] = len(data)
    
    p = ptr+2
    for c in data:
        MINI_GIGA_HEAP[p] = ord(c)
        p += 1
    
    # TODO create another object? for secret info
    if data[:4] == "SEC:":
        (c1, c2) = crc16(data)
        MINI_GIGA_HEAP[p] = c1
        p += 1
        MINI_GIGA_HEAP[p] = c2
    return ptr
        
def print_heap_state():
    global heap_list, MINI_GIGA_HEAP
    print("\n\nHeap state:")
    print("-"*20)
    for i in range(len(heap_list)):
        print("Heap element address: ", heap_list[i])
        print("Type:\t %x" % MINI_GIGA_HEAP[heap_list[i]])  
        print("Len:\t", MINI_GIGA_HEAP[heap_list[i]+1]) 
        print([hex(x) for x in MINI_GIGA_HEAP[heap_list[i]+2:heap_list[i]+2+4]])
    print("-"*20)

def ctf_loop():
    while True:
        try:
            line = input('8==> ')
            print("# ", end="")
            if 'q' == line.rstrip():
                break

            elif 'init_crypto' == line.rstrip() or 'ic' == line.rstrip():
                init_crypto()
                continue
            
            elif 'terminate_crypto' == line.rstrip() or 'tc' == line.rstrip():
                crypto_terminate()
                continue
                
            elif 'store ' == line.rstrip()[:6]:
                ptr = store_info(line.rstrip()[6:])
                print("Info object pointer:\t", ptr)
                
            elif 'read ' == line.rstrip()[:5]:
                ptr = -1
                try:
                    ptr = int(line.rstrip()[5:])
                except:
                    print("Not an integer")
                    continue
                print(ptr)
                read_info(ptr)
                
            elif 'remove ' == line.rstrip()[:7]:
                ptr = -1
                try:
                    ptr = int(line.rstrip()[7:])
                except:
                    print("Not an integer")
                    continue
                print(ptr)
                remove_info(ptr)
            elif 'help' == line.rstrip() or '?' == line.rstrip():
                print("Usage:")
                print("\thelp\t - to print help")
                print("\treset\t - soft reset chip")
                print("\tabout\t - to print info about the program")
            elif 'about' == line.rstrip():
                print("\nRiscuFEFE CTF 2023")
                print("All writes preserved")
                print("OSS components on https://github.com/XXX")
            
            elif 'reset' == line.strip():
                return True
            else:
                print("Illegal and dishonest command")
        except Exception as e:
            print("Illegal and dishonest command")
        except KeyboardInterrupt as e:
            print("Illegal and dishonest command")


def ctf_main():
    global CRYPTO_INIT, HANDLE_TO_SECRET
    while True:
        CRYPTO_INIT = False
        HANDLE_TO_SECRET = -1
        init_heap()
        init_crypto()
        print("***Welcome to secure object store shell***")

        if not ctf_loop():
            break
