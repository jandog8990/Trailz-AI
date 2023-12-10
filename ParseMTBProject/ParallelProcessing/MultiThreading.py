import threading

# concurrent execution of multiple threads within 
# a single process. Threads share the same memory
# space, they can execute indep. tasks simultaneous.
def print_numbers():
    for i in range(1, 6):
        print(i)

def print_letters():
    for letter in ['A', 'B', 'C', 'D', 'E']:
        print(letter)

if __name__ == '__main__':
    t1 = threading.Thread(target=print_numbers)
    t2 = threading.Thread(target=print_letters)

    t1.start()
    t2.start()
    t1.join()
    t2.join()
