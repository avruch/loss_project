#include <uapi/linux/bpf.h>
#include <linux/in.h>
#include <linux/if_ether.h>
#include <linux/if_packet.h>
#include <linux/if_vlan.h>
#include <linux/ip.h>
#include <linux/ipv6.h>

//___________________________________BPF_Maps___________________________________//
//BPF_TABLE( MAPTYPE, uint32_t, long, dropcnt, 1); // general table
BPF_ARRAY(user_param, int, 2);// user_param[0] =random loss rate, user_param[1] =poissn loss rate
BPF_ARRAY(random_param, int, 100); //
BPF_ARRAY(drop_cnt2, long, 1);//for prog_2
//______________________________________________________________________________//
int drop_func(struct xdp_md *ctx) {
    int rc = 0;
    uint32_t index=0;
    long *counter ;
    int *drop_val;
    int *param;
    counter=drop_cnt2.lookup(&index);
    drop_val=user_param.lookup(&index);
    param=random_param.lookup(&index);
    if(!drop_val){
        return 0;
    }
    if(!param ){
        return 0;
    }
    if(counter) {
        //bpf_trace_printk("drop_val! %d", *drop_val);
        u32 randd= bpf_get_prandom_u32();
        int randdd =randd % 100; //FIXME change to 100,000 for mili percent
        random_param.update(&index, &randdd);
        if(*param < *drop_val){
           bpf_trace_printk("drop! %d", *counter);
           rc= XDP_DROP;
           }
        else{
             rc=XDP_PASS;
             }
        __sync_fetch_and_add(counter, 1);
        }
return rc;
}


