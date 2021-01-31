#!/bin/bash

#Author: Ariwori  i@wqlin.com https://wqlin.com
DST_HOME="${HOME}/DST"
dst_conf_dirname="DoNotStarveTogether"
dst_conf_basedir="${DST_HOME}/Klei"
dst_base_dir="${dst_conf_basedir}/${dst_conf_dirname}"
dst_server_dir="${DST_HOME}/DSTServer"
dst_bin_cmd="./dontstarve_dedicated_server_nullrenderer"
data_dir="${DST_HOME}/dstscript"
dst_token_file="${data_dir}/clustertoken.txt"
server_conf_file="${data_dir}/server.conf"
dst_cluster_file="${data_dir}/clusterdata.txt"
log_arr_str="${data_dir}/logarr.txt"
ays_log_file="${data_dir}/ays_log_file.txt"
log_save_dir="${dst_conf_basedir}/LogBackup"
mod_cfg_dir="${data_dir}/modconfigure"
cluster_backup_dir="${dst_conf_basedir}/ClusterBackup"
feed_back_link="https://wqlin.com/archives/157.html"
script_url='https://tools.wqlin.com/dst/dstserver.sh'
my_api_link="https://tools.wqlin.com/dst/dst.php"

cluster=$1
shardarray=($2)

# 屏幕输出
info(){
  echo "[信息] $1"
}
tip(){
  echo "[提示] $1"
}
error(){
  echo "[错误] $1"
}

Setup_mod(){
  if [ -f "${data_dir}/mods_setup.lua" ]
  then
    rm -rf "${data_dir}/mods_setup.lua"
  fi
  touch "${data_dir}/mods_setup.lua"
  shard=${shardarray[0]}
  dir=$(cat "${dst_base_dir}/${cluster}/${shard}/modoverrides.lua" | grep "workshop" | cut -f2 -d '"' | cut -d "-" -f2)
  for moddir in ${dir}
  do
    if [ $(grep "${moddir}" -c "${data_dir}/mods_setup.lua") -eq 0 ]
    then
	    echo "ServerModSetup(\"${moddir}\")" >> "${data_dir}/mods_setup.lua"
    fi
  done
  cp "${data_dir}/mods_setup.lua" "${dst_server_dir}/mods/dedicated_server_mods_setup.lua"
  info "添加启用的MODID到MOD更新配置文件！"
}


Setup_mod
cd "${dst_server_dir}/bin"
for shard in ${shardarray}
do
    unset TMUX
    tmux new-session -s DST_${shard} -d "${dst_bin_cmd} -persistent_storage_root ${dst_conf_basedir} -conf_dir ${dst_conf_dirname} -cluster ${cluster} -shard ${shard}"
done
