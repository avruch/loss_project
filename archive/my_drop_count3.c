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
//BPF_ARRAY(drop_cnt, long, 1);//for prog_1
BPF_ARRAY(drop_cnt2, long, 1);//for prog_2
BPF_PERCPU_ARRAY(drop_cnt, long, 1);
//______________________________________________________________________________//

//bpf_trace_printk("rand! %d", randdd); //how to print int
//bpf_trace_printk("param! %d", *param); //how to print int *

int xdp_prog1(struct xdp_md *ctx) {
    uint32_t index=0;
    long DROP_PARAMETER=4;
    // drop packets
    int rc = 0; // let pass XDP_PASS or redirect to tx via XDP_TX
    long *counter;
    counter=drop_cnt2.lookup(&index);
    if(counter) {
        if( *counter == DROP_PARAMETER ) {
            rc = XDP_DROP;
            __sync_fetch_and_sub(counter, DROP_PARAMETER);
            return rc;
            }
        else {
            rc=XDP_PASS;
            __sync_fetch_and_add(counter, 1);
             return rc;
            }
        }
    return rc;
}



int random_func(struct xdp_md *ctx) {
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
        int randdd =randd % 100;
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
int poisson_func(struct xdp_md *ctx) {
    int rc = 0;
    uint32_t index=0;
    uint32_t param_inedx=1;
    long *counter ;
    int *drop_val;
    counter=drop_cnt2.lookup(&index);
    drop_val=user_param.lookup(&param_inedx);
    if(!drop_val){
        return 0;
    }
    if(counter) {
    bpf_trace_printk("drop_val= %d", *drop_val);
    bpf_trace_printk("drop counter= %d", *counter);
        if( *counter <= *drop_val ) {
            rc = XDP_DROP;
            //bpf_trace_printk("drop counter= %d", *counter);
            *counter +=1;
            }
        else {
            rc=XDP_PASS;
            *counter +=1;

            }
        }
    return rc;
}

