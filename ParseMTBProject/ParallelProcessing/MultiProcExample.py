import multiprocessing

def square(x):
    return x**2

if __name__ == '__main__':
    numbers = [1,2,3,4,5]

    with multiprocessing.Pool() as pool:
        result = pool.map(square, numbers)

    print(result)
