#include <uapi/linux/bpf.h>
#include <linux/in.h>
#include <linux/if_ether.h>
#include <linux/if_packet.h>
#include <linux/if_vlan.h>
#include <linux/ip.h>
#include <linux/ipv6.h>
//#include <stdlib.h>

BPF_TABLE( MAPTYPE, uint32_t, long, dropcnt, 1);

int xdp_prog1(struct xdp_md *ctx) {
    long DROP_PARAMETER=4;
    // drop packets
    int rc = 0; // let pass XDP_PASS or redirect to tx via XDP_TX

    uint32_t index=0;
    long *counter;
    counter=dropcnt.lookup(&index);
    if(counter) {
        if( *counter == DROP_PARAMETER ) {
            rc = XDP_DROP;
            __sync_fetch_and_sub(counter, DROP_PARAMETER);
            }
        else {
            rc=XDP_PASS;
            __sync_fetch_and_add(counter, 1);
            }
        }

    return rc;
}
/*
int xdp_prog2(struct xdp_md *ctx,int percantge) {
    long DROP_PARAMETER_2=percantge;
    // drop packets
    int rc = 0; // let pass XDP_PASS or redirect to tx via XDP_TX
    uint32_t index=0;
    int arr[DROP_PARAMETER_2]=0;
    for (int i;i<DROP_PARAMETER_2;i++){
        arr[i]= rand() % 100;
    }
    long *counter;
    counter=dropcnt.lookup(&index);
    if(counter) {
        for (int i;i<DROP_PARAMETER_2;i++){
          if( *counter ==  arr[i] ) {
            rc = XDP_DROP;
            }
           else {
            rc=XDP_PASS;
            }
        }
        __sync_fetch_and_add(counter, 1);
        if( *counter ==  100) {
        __sync_fetch_and_sub(counter, 100);
        }
    }
    return rc;
}
*/

int xdp_prog3(struct xdp_md *ctx) {
    int DROP_PARAMETER_3=100000;
    // drop packets
    int rc = 0; // let pass XDP_PASS or redirect to tx via XDP_T
    int i=0;
    while(i<DROP_PARAMETER_3){
        i++;
    }
    rc=XDP_PASS;
    return rc;
}