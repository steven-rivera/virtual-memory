import argparse
from collections import deque


INIT_FILE         = "init-no-dp.txt"
INPUT_FILE        = "input-no-dp.txt"
NUM_FRAMES        = 1024
FRAME_SIZE        = 512
PHYSICAL_MEM_SIZE = NUM_FRAMES * FRAME_SIZE
PM                = [0] * PHYSICAL_MEM_SIZE
DISK              = [ [0]*FRAME_SIZE for _ in range(NUM_FRAMES) ]
FREE_FRAMES       = deque(range(2, FRAME_SIZE))


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--withoutdp", action="store_true", help="run without demand paging")
    
    args = vars(parser.parse_args())
    
    if args["withoutdp"]:
        print("Running without")
        initialize_PM_without_demand_paging()
        translate_VAs_to_PAs_without_demand_paging()
    else:
        print("Running with DP")
        initialize_PM_with_demand_paging()
        translate_VAs_to_PAs_with_demand_paging()




def initialize_PM_without_demand_paging():
    global PM

    with open(INIT_FILE, "r") as f:
        st_line = f.readline().strip().split()
        pt_line = f.readline().strip().split()

        
        # Parse st_line
        for index in range(0, len(st_line), 3):
            segment         = int( st_line[index] )
            segment_length  = int( st_line[index + 1] )
            pt_frame        = int( st_line[index + 2] )

            # Set segment length
            PM[2*segment] = segment_length

            # Set frame the the page table of segment resides in
            PM[(2*segment) + 1] = pt_frame

        
        # Parse pt_line
        for index in range(0, len(pt_line), 3):
            segment      = int( pt_line[index] )
            page         = int( pt_line[index + 1] )
            page_frame   = int( pt_line[index + 2] )

            # Set the frame that the page p of segment s resides in
            pt_frame = PM[(2*segment) + 1]
            PM[(pt_frame * FRAME_SIZE) + page] = page_frame
                    

       
                    
def initialize_PM_with_demand_paging():
    global PM
    global FREE_FRAMES
    global DISK

    with open(INIT_FILE, "r") as f:
        st_line = f.readline().strip().split()
        pt_line = f.readline().strip().split()

        
        # Parse st_line
        for index in range(0, len(st_line), 3):
            segment         = int( st_line[index] )
            segment_length  = int( st_line[index + 1] )
            pt_frame        = int( st_line[index + 2] )

            # Set segment length
            PM[2*segment] = segment_length

            # Set frame the the page table of segment resides in
            PM[(2*segment) + 1] = pt_frame

            if pt_frame > 0:
                FREE_FRAMES.remove(pt_frame)

        # Parse pt_line
        for index in range(0, len(pt_line), 3):
            segment      = int( pt_line[index] )
            page         = int( pt_line[index + 1] )
            page_frame   = int( pt_line[index + 2] )

            # Set the frame that the page p of segment s resides in
            pt_frame = PM[(2*segment) + 1]

            if pt_frame < 0:
                DISK[abs(pt_frame)][page] = page_frame
            else:
                PM[(pt_frame * FRAME_SIZE) + page] = page_frame

            if page_frame > 0:
                FREE_FRAMES.remove(page_frame)



def translate_VAs_to_PAs_without_demand_paging():
    global PM

    with open(INPUT_FILE, "r") as f:
        VAs = f.readline().strip().split()

        mask_9bit = 0b1_1111_1111
        mask_18bit = 0b11_1111_1111_1111_1111

        for va in VAs:
            va = int(va)

            # Right shift 18 bits because p and w are both 9 bits
            s = va >> 18  

            # Right shift 9 bits to get rid of w and bitwise AND with first 9 bits
            p = (va >> 9) & mask_9bit

            # Bitwise AND with first 9 bits to get w
            w = va & mask_9bit

            # Bitwise AND with first 18 bits to get pw (pw = p*FRAME_SIZE + w)
            pw = va & mask_18bit

            print(f"s:{s}, p:{p}, w:{w}, pw:{pw}")
            # print(f"s:{s:b}, p:{p:b}, w:{w:b}, pw:{pw:b}")

            segment_size = PM[2*s]
            if pw >= segment_size:
                print("-1")
                continue

            page_table_frame = PM[(2*s) + 1]
            page_frame = (page_table_frame*FRAME_SIZE) + p
            PA = (PM[page_frame]*FRAME_SIZE) + w
            print(PA)




def translate_VAs_to_PAs_with_demand_paging():
    global PM
    global FREE_FRAMES

    with open(INPUT_FILE, "r") as f:
        VAs = f.readline().strip().split()

        mask_9bit = 0b1_1111_1111
        mask_18bit = 0b11_1111_1111_1111_1111

        for va in VAs:
            va = int(va)

            # Right shift 18 bits because p and w are both 9 bits
            s = va >> 18  

            # Right shift 9 bits to get rid of w and bitwise AND with first 9 bits
            p = (va >> 9) & mask_9bit

            # Bitwise AND with first 9 bits to get w
            w = va & mask_9bit

            # Bitwise AND with first 18 bits to get pw (pw = p*FRAME_SIZE + w)
            pw = va & mask_18bit

            segment_size = PM[2*s]
            if pw >= segment_size:
                print("-1")
                continue

            page_table_frame = PM[(2*s) + 1]
            page_frame = (page_table_frame*FRAME_SIZE) + p

            if page_frame < 0:
                free_frame = FREE_FRAMES.popleft()
                page_frame = free_frame
                PA = (PM[page_frame]*FRAME_SIZE) + w





            # if page_table_frame < 0:
            #     free_frame = FREE_FRAMES.popleft()





if __name__ == "__main__":
    main()
