PHYSICAL_MEMORY_SIZE = 524288
FRAME_SIZE = 512



def init():
    with open("init.txt", "r") as f:
        line1 = f.readline().strip().split()
        line2 = f.readline().strip().split()

        for index in range(0, len(line1), 3):
            print(index)

        print(type(line1), line1)
        print(type(line2), line2)



if __name__ == "__main__":
    init()