#!/bin/bash

#Author: Ariwori  i@wqlin.com https://wqlin.com
DST_HOME="${HOME}/DST"
dst_server_dir="${DST_HOME}/DSTServer"
dst_logs_dir=$1

# Install steamcmd
Install_Steamcmd(){
  if [ ! -f ${DST_HOME}/steamcmd_linux.tar.gz ]
  then
    wget "https://steamcdn-a.akamaihd.net/client/installer/steamcmd_linux.tar.gz" -O "${DST_HOME}/steamcmd_linux.tar.gz"
  fi
  if [ ! -f ${DST_HOME}/steamcmd/steamcmd.sh ]
  then
    mkdir -p "${DST_HOME}/steamcmd"
    tar -xzvf "${DST_HOME}/steamcmd_linux.tar.gz" -C "${DST_HOME}/steamcmd"
    chmod +x "${DST_HOME}/steamcmd/steamcmd.sh"
  fi
  if [ ! -f ${DST_HOME}/.steam/sdk32/steamclient.so ]
  then
    mkdir -p "${DST_HOME}/.steam/sdk32"
    cp "${DST_HOME}/steamcmd/linux32/steamclient.so" "${DST_HOME}/.steam/sdk32/steamclient.so"
  fi
}
# Install DST Dedicated Server
Install_Game(){
  if [[ $1 != "public" ]]
  then
    beta_str="-beta $2 "
  else
    beta_str=""
  fi
  cd "${DST_HOME}/steamcmd" || exit 1
  ./steamcmd.sh +@ShutdownOnFailedCommand 1 +login anonymous +force_install_dir "${dst_server_dir}" +app_update "343050" ${beta_str}validate +quit
  if [ ! -f "${dst_server_dir}/bin/lib32/libcurl-gnutls.so.4" ]
  then
    ln -s "/usr/lib/libcurl.so.4" "${dst_server_dir}/bin/lib32/libcurl-gnutls.so.4"
  fi
  cd ${HOME}
}

rm -rf ${dst_logs_dir}/dst.log

touch ${dst_logs_dir}/running

Install_Steamcmd >> ${dst_logs_dir}/dst.log

case $2 in
install)
Install_Game $3 $4 >> ${dst_logs_dir}/dst.log
echo "操作完成！" >> ${dst_logs_dir}/dst.log
;;
uninstall)
for dir in $(ls ${dst_server_dir})
do
    if [[ $dir != "mods" ]]
    then
        rm -rvf ${dst_server_dir}/$dir >> ${dst_logs_dir}/dst.log
    fi
done
echo "卸载完成！" >> ${dst_logs_dir}/dst.log
;;
*)
echo "usage install|uninstall"
exit 1
;;
esac
rm -rf ${dst_logs_dir}/running