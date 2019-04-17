#!/bin/sh
#
# Desc: restore backup config to k8s cluster
# usage: ./k8s_restore.sh /k8s_backup_dir
#
# Auther: farmer.luo@gmail.com
# Date: 2019.4.16
#

# skip namespace in k8s cluster system and cluster role binding
exclude=("default" "kube-public" "kube-system" "cluster")

function exec_restore() {

    items=("namespace" "secret" "configmap" "serviceaccount" "rolebinding" "deployment" "daemonset" "statefulset" "service" "ingress" "horizontal_pod_autoscaler")

    for i in ${items[@]}
    do
        if [ -d $1/$i ]; then
           echo "kubectl apply -f $1/$i/"
           kubectl apply -f $1/$i/
        fi
    done

}


for i in `ls ${1}`
do
    echo "${exclude[@]}" | grep -wq "$i" && continue 
    exec_restore "$1/$i"
done
