import sys
import argparse


INIT_FILE = "init.txt"
INPUT_FILE = "input.txt"
PHYSICAL_MEMORY_SIZE = 524288
FRAME_SIZE = 512
PM = [None] * PHYSICAL_MEMORY_SIZE


def main():
    
    # Initialize physical memory from init file
    initialize_PM()

    parser = argparse.ArgumentParser()
    parser.add_argument("--withoutdp", action="store_true", help="run without demand paging")
    
    args = vars(parser.parse_args())
    
    if args["withoutdp"]:
        print("Running without")
        translate_VAs_to_PAs_without_demand_paging()
    else:
        print("Running with DP")
        translate_VAs_to_PAs_with_demand_paging()




def initialize_PM():
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
    with open("input.txt", "r") as f:
        VAs = f.readline().strip().split()

        mask_9bit = 0b1_1111_1111
        mask_18bit = 0b11_1111_1111_1111_1111

        # TODO




if __name__ == "__main__":
    main()
