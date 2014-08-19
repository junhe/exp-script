#include <stdio.h>
#include <linux/types.h>
#include <stdlib.h>
#include <string.h>

#define NBLOCKS 15

struct ext4_extent_header {
         __le16  eh_magic;       /* probably will support different formats */
         __le16  eh_entries;     /* number of valid entries */
         __le16  eh_max;         /* capacity of store in entries */
         __le16  eh_depth;       /* has tree real underlying blocks? */
         __le32  eh_generation;  /* generation of the tree */
};

struct ext4_extent {
         __le32  ee_block;       /* first logical block extent covers */
         __le16  ee_len;         /* number of blocks covered by extent */
         __le16  ee_start_hi;    /* high 16 bits of physical block */
         __le32  ee_start_lo;    /* low 32 bits of physical block */
 };
 
struct ext4_extent_idx {
        __le32  ei_block;       /* index covers logical blocks from 'block' */
        __le32  ei_leaf_lo;     /* pointer to the physical block of the next *
                                 * level. leaf or next index could be there */
        __le16  ei_leaf_hi;     /* high 16 bits of physical block */
        __u16   ei_unused;
};

static void modify_u32(char *com, const char *prompt,                                                                                                                                
                   const char *format, __u32 *val)                                                                                                                                       
{                                                                                                                                                                                    
    char buf[200];                                                                                                                                                                   
    unsigned long v;                                                                                                                                                                 
    char *tmp;                                                                                                                                                                       
                                                                                                                                                                                     
    sprintf(buf, format, *val);                                                                                                                                                      
    printf("%30s    [%s] ", prompt, buf);                                                                                                                                            
    if (!fgets(buf, sizeof(buf), stdin))                                                                                                                                             
        return;                                                                                                                                                                      
    if (buf[strlen (buf) - 1] == '\n')                                                                                                                                               
        buf[strlen (buf) - 1] = '\0';                                                                                                                                                
    if (!buf[0])                                                                                                                                                                     
        return;                                                                                                                                                                      
    v = strtoul(buf, &tmp, 0);                                                                                                                                                       
    if (*tmp)                                                                                                                                                                        
        printf("error\n");
    else                                                                                                                                                                             
        *val = v;                                                                                                                                                                    
}                                                                                                                                                                                    

void print_blocks(__le32 *p)
{
    int i;
    for ( i = 0; i < NBLOCKS; i++ ) {
        /*printf("%d(0x%x)\n", p[i], p[i]);*/
        printf("%d\n", p[i]);
    }
}

int main(int argc, char **argv)
{
    __le32  i_block[NBLOCKS];
    int i;
    char *tmp;

    struct ext4_extent_header *p_header = \
        (struct ext4_extent_header *) i_block;
    struct ext4_extent *p_extent = \
        (struct ext4_extent *) (p_header + 1);

    /*printf("sizeof(unsigned long):%lu\n", sizeof(unsigned long)); [> 8 <]*/
    /*printf("sizeof(__le32):%lu\n", sizeof(__le32)); [> 4 <]*/

    if ( argc != 14 ) {
        printf("Usage: ./me n-entries" 
                " logical len physical"
                " logical len physical"
                " logical len physical"
                " logical len physical\n");
        return 1;
    }

    memset(i_block, 0, 60);

    p_header->eh_magic      = 0xF30A; 
    p_header->eh_entries    = strtoul(argv[1], &tmp, 0);
    /*printf("nentry:%u\n", p_header->eh_entries);*/
    p_header->eh_max        = 4;
    p_header->eh_depth      = 0;
    p_header->eh_generation = 0;

    for ( i = 0; i < 4; i++ ) {
        p_extent[i].ee_block = strtoul(argv[3*i+2], &tmp, 0);
        p_extent[i].ee_len   = strtoul(argv[3*i+3], &tmp, 0);
        unsigned long long phyblock = strtoul(argv[3*i+4], &tmp, 0);
        p_extent[i].ee_start_lo  = phyblock & 0xffffffff;
        p_extent[i].ee_start_hi  = (phyblock >> 32) & 0x0000ffff;
        /*printf("extent logical:%u, len:%u, physical:%lu\n",*/
                /*p_extent[i].ee_block,*/
                /*p_extent[i].ee_len,*/
                /*( ((unsigned long)p_extent[i].ee_start_hi << 32))*/
                  /*| p_extent[i].ee_start_lo);*/
    }


    /*printf("p_header: %p\n", p_header);*/
    /*printf("p_extent: %p\n", p_extent);*/

    print_blocks(i_block);
}


