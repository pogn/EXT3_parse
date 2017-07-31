import sys
import struct
import math
def FileInfo(group_num, inode_num, root):
    ######Group Descipter Table######
    #group_num = 0 #0~7
    f.seek(offset_GDT(Block_size_B))
    f.seek(group_num*32,1)
    sp = f.read(32*Group_cnt)
    intable_addr_BL = struct.unpack_from("<I", sp, 0x8)[0]
    #print "inodeaddr",hex(intable_addr_BL)
    
    ######Inode Table + root inode#########
    f.seek(intable_addr_BL * Block_size_B)# + Inode_size)
    f.seek(Inode_size*inode_num,1)
    sp = f.read(Inode_size)

    
    file_size = struct.unpack_from("<I", sp, 0x4)[0]
    if root ==0:
                print "     ",
    print "     file_size",hex(file_size)
    
    ###block pointers->directory Entry(size : 4*15=60)
    i=0
    
    while 1:
        block_pointer = struct.unpack_from("<I", sp, 0x28+i)[0]
        
        if root ==0:
                print "     ",
        print "     blockPoiter",hex(block_pointer)
        if block_pointer==0:
           break
        i=i+4
        break
    return
    
def ReadInode(group_num, inode_num, root):
    ######Group Descipter Table######
    #group_num = 0 #0~7
    f.seek(offset_GDT(Block_size_B))
    f.seek(group_num*32,1)
    sp = f.read(32*Group_cnt)
    intable_addr_BL = struct.unpack_from("<I", sp, 0x8)[0]
    
    ######Inode Table + root inode#########
    #inode_num = 1 #second one is ROOT  0~
    f.seek(intable_addr_BL * Block_size_B)# + Inode_size)
    f.seek(Inode_size*inode_num,1)
    sp = f.read(Inode_size)

    file_size = struct.unpack_from("<I", sp, 0x4)[0]
    '''
    if file_size <= 0xC000: #direct block only
        inode_addr1 = struct.unpack_from("<I", sp, 0x28)[0]
        print hex(inode_addr1)
    else :
        print "not yet supported - indirec block"
    '''
    ###block pointers->directory Entry(size : 4*15=60)
    i=0
    while 1:
        #if block_pointer==0:
        #   break
        block_pointer = struct.unpack_from("<I", sp, 0x28+i)[0]
        i=i+4
        break
    
    f.seek(block_pointer*4096)
    sp=f.read(0x0C)
    k=0
    fp_rlen=0
    while 1:
        Inode = struct.unpack_from("<I", sp, 0x0)[0]
        record_len = struct.unpack_from("<H", sp, 0x4)[0]
        name_len = struct.unpack_from("<c", sp, 0x6)[0]
        file_type = struct.unpack_from("<c", sp, 0x7)[0]
        file_type = ord(file_type)
        name_len = ord(name_len)
        
        fn.seek(block_pointer*4096 + 0x08 +  fp_rlen)
        name=fn.read(record_len - 8)
        name = name[:name_len]
    
        if root ==0:
                print "     ",
        if file_type == 0x02 : #dir
            print "DIR:",name
            if k == 4 : #only for dir2
                Inode=Inode-1
                whatB=Inode/Inodes_per_group
                whatI=Inode%Inodes_per_group
                ReadInode(whatB,whatI,0)
        elif file_type == 0x01 : #file
            print "file :", name
            Inode=Inode-1
            whatB=Inode/Inodes_per_group
            whatI=Inode%Inodes_per_group
            FileInfo(whatB,whatI,root)
            if root == 0 : 
                return
        
        fp_rlen=fp_rlen + record_len
        #next
        sp=f.seek(block_pointer*4096 +fp_rlen+8)
        record_len=f.read(1)
        record_len=ord(record_len)

        sp=f.seek(block_pointer*4096 +fp_rlen)
        sp=f.read(record_len)
    
        k=k+1
        if k ==7 :
            break
    return

def offset_GDT(bsize):
    if bsize ==4096 :
        return 4096
    else:
        return 2048
    
#f = open(sys.argv[1], "rb")

f=open("ext3.dd","rb")
fn=open("ext3.dd","rb")
f.seek(1024)

#####Super Block#####
sp = f.read(1024)

total_block = struct.unpack_from("<I", sp, 0x4)[0]
#print("total block: ", hex(total_block), total_block)
blocks_per_group = struct.unpack_from("<I", sp, 0x20)[0]
#print("blocks_per_group: ", hex(blocks_per_group), blocks_per_group)
Group_cnt = total_block / blocks_per_group

Inode_size = struct.unpack_from("<H", sp, 0x58)[0]
Inodes_per_group = struct.unpack_from("<I", sp, 0x28)[0]

log_Bsize = struct.unpack_from("<I", sp, 0x18)[0]
Block_size_B = pow(2, 10+log_Bsize)

ReadInode(0,1,1)
