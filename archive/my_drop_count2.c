#include <uapi/linux/bpf.h>
#include <linux/in.h>
#include <linux/if_ether.h>
#include <linux/if_packet.h>
#include <linux/if_vlan.h>
#include <linux/ip.h>
#include <linux/ipv6.h>



//___________________________________BPF_Maps___________________________________//
//BPF_TABLE( MAPTYPE, uint32_t, long, dropcnt, 1); // general table
BPF_ARRAY(user_param, int, 1);
BPF_ARRAY(random_param, int, 100);
BPF_ARRAY(drop_cnt, long, 1);//for prog_1
BPF_ARRAY(drop_cnt2, long, 1);//for prog_2
//______________________________________________________________________________//

//bpf_trace_printk("rand! %d", randdd); //how to print int
//bpf_trace_printk("param! %d", *param); //how to print int *

int xdp_prog1(struct xdp_md *ctx) {
    uint32_t index=0;
    long DROP_PARAMETER=4;
    // drop packets
    int rc = 0; // let pass XDP_PASS or redirect to tx via XDP_TX
    long *counter;
    counter=drop_cnt.lookup(&index);
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

int xdp_prog2(struct xdp_md *ctx) {
    int rc = 0;
    uint32_t index=0;
    uint32_t param_index=0;
    long *counter2 ;
    int *drop_val;
    int *param;
    counter2=drop_cnt2.lookup(&index);
    drop_val=user_param.lookup(&index);
    param=random_param.lookup(&index);
    if(!drop_val){
        return 0;
    }
    if(!param ){
        return 0;
    }

    if(counter2) {
        char DROP_PARAMETER_2=*drop_val;
        bpf_trace_printk("count! %d", *counter2);
        if(*counter2==0){
                    for(char i=0;i<DROP_PARAMETER_2;i++){
                        u32 randd= bpf_get_prandom_u32();
                        int randdd =randd % 100;
                        random_param.update(&index, &randdd);
                        //bpf_trace_printk("index! %u", index);
                        index=index+1;
                        }
        }
          for(char i=0;i<DROP_PARAMETER_2;i++){
                int *temp_param;
                temp_param=random_param.lookup(&param_index);
                    if(!temp_param){
                        return 0;
                    }
                //bpf_trace_printk("index! %u", param_index);
                //bpf_trace_printk("param! %u", *temp_param);
                param_index=param_index+1;
                if(*counter2 == *temp_param){
                    bpf_trace_printk("drop! %d", *counter2);
                    rc= XDP_DROP;
                }
                else{
                rc=XDP_PASS;
                }
          }
          __sync_fetch_and_add(counter2, 1);
          if( *counter2 ==  100) {
          __sync_fetch_and_sub(counter2, 100);
          }
    }
return rc;
}

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
