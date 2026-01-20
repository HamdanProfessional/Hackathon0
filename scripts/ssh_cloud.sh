#!/usr/bin/env expect -f
set timeout 30
set password "NooBNooBl0l!"
spawn ssh -o StrictHostKeyChecking=no root@143.244.143.143 {lassign}[lindex $argv 0]
expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    eof
}
