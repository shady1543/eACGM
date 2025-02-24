#!/bin/bash

sudo tcpdump -i any port 11434 -n -l | awk '
BEGIN {
    start_time = systime()
    packets = 0
    inp = 0
    out = 0
}
{
    if ($3 == "In"){
        inp++
    }else{
        out++
    }
    packets++
    current_time = systime()
    table[$5]++
    dest = substr($7, 1, length($7) - 1)
    table[dest]++
    if (current_time - start_time >= 5) {
        start_time = current_time
        timestamp = strftime("%Y-%m-%d %H:%M:%S", current_time)
        print current_time,  packets >> "trace.txt"
        print inp, out >> "trace.txt"
        
        for (i in table) {
            print i, table[i] >> "trace.txt"
        }
        print "---" >> "trace.txt"
        fflush("trace.txt")
        packets = 0
        inp=0
        out=0
        delete table
    }
}' 
