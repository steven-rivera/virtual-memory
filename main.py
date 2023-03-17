import argparse
from collections import deque


INIT_FILE         = ""
INPUT_FILE        = ""
NUM_FRAMES        = 1024
FRAME_SIZE        = 512
PHYSICAL_MEM_SIZE = NUM_FRAMES * FRAME_SIZE
PM                = [0] * PHYSICAL_MEM_SIZE
DISK              = [ [0] * FRAME_SIZE for _ in range(NUM_FRAMES) ]
FREE_FRAMES       = deque(range(2, FRAME_SIZE))
DEBUG             = False


def main():
    global INIT_FILE
    global INPUT_FILE 

    parser = argparse.ArgumentParser()
    parser.add_argument("init_file",  help="file for initializing memory")
    parser.add_argument("input_file", help="file containing virtual addresses to translate")
    parser.add_argument("--withoutdp", action="store_true", help="run without demand paging")
    
    args = vars(parser.parse_args())
    
    INIT_FILE = args["init_file"]
    INPUT_FILE = args["input_file"]

    if args["withoutdp"]:
        print("Running WITHOUT demand paging")
        initialize_PM_without_demand_paging()
        translate_VAs_to_PAs_without_demand_paging()
    else:
        print("Running WITH demand paging")
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




def translate_VAs_to_PAs_without_demand_paging():
    global PM

    with open("output-no-dp.txt", "w") as o:
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

                if DEBUG: print(f"s:{s}, p:{p}, w:{w}, pw:{pw}")

                segment_size = PM[2*s]
                if pw >= segment_size:
                    o.write("-1 ")
                    continue

                page_table_frame = PM[(2*s) + 1]
                page_frame_mem_address = (page_table_frame*FRAME_SIZE) + p
                PA = (PM[page_frame_mem_address]*FRAME_SIZE) + w
                o.write(f"{PA} ")
       



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

            # If page table frame is in memory, remove it from free frames list
            if pt_frame > 0:
                FREE_FRAMES.remove(pt_frame)

            # Set segment length
            PM[2*segment] = segment_length

            # Set frame the the page table of segment resides in
            PM[(2*segment) + 1] = pt_frame

            

        # Parse pt_line
        for index in range(0, len(pt_line), 3):
            segment      = int( pt_line[index] )
            page         = int( pt_line[index + 1] )
            page_frame   = int( pt_line[index + 2] )

            # If page frame of page is in memory, remove it from free frames list
            if page_frame > 0:
                FREE_FRAMES.remove(page_frame)

            
            pt_frame = PM[(2*segment) + 1]

            if pt_frame < 0:
                DISK[abs(pt_frame)][page] = page_frame
            else:
                # Set the frame that the page p of segment s resides in
                PM[(pt_frame * FRAME_SIZE) + page] = page_frame

    



def translate_VAs_to_PAs_with_demand_paging():
    global PM
    global FREE_FRAMES

    with open("output-dp.txt", "w") as o:
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

                if DEBUG: print(f"s:{s}, p:{p}, w:{w}, pw:{pw}")


                segment_size = PM[2*s]
                if pw >= segment_size:
                    o.write("-1 ")
                    continue

                page_table_frame = PM[(2*s) + 1]
                if DEBUG: print("page_table_frame:", page_table_frame, end=" ")
                
                if page_table_frame < 0:
                    # If page table not in memory allocate free frame and copy block from disk to PM
                    free_page_table_frame = FREE_FRAMES.popleft()
                    copy_block_to_PM(abs(page_table_frame), free_page_table_frame)
                    PM[(2*s) + 1] = free_page_table_frame
                    page_table_frame = free_page_table_frame


                page_frame_mem_address = (page_table_frame*FRAME_SIZE) + p
                page_frame = PM[page_frame_mem_address]
                
                if DEBUG: print("page_frame_mem_address:", page_frame_mem_address, end=" ")
                if DEBUG: print("page_frame:", page_frame)
                
                if page_frame < 0:
                    # If page frame of page p not in memory allocate free frame
                    free_frame = FREE_FRAMES.popleft()
                    PM[page_frame_mem_address] = free_frame
                    page_frame = free_frame
                    
                PA = (page_frame*FRAME_SIZE) + w
                o.write(f"{PA} ")




def copy_block_to_PM(block_frame, free_frame):
    global DISK
    global PM

    block = DISK[block_frame]
    starting_PM_address = free_frame * FRAME_SIZE
    
    for index, value in enumerate(block):
        PM[starting_PM_address + index] = value




if __name__ == "__main__":
    main()
