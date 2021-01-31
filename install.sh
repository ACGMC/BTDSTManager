#!/bin/bash
PATH=/www/server/panel/pyenv/bin:/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

#配置插件安装目录
install_path=/www/server/panel/plugin/dst_manager

#宝塔插件图标路径
panel_static_path=/www/server/panel/BTPanel/static/img/soft_ico

# 检查当前系统信息
Check_sys(){
  if [[ -f "/etc/redhat-release" ]]
  then
    release="centos"
  elif cat /etc/issue | grep -q -E -i "debian"
  then
    release="debian"
  elif cat /etc/issue | grep -q -E -i "ubuntu"
  then
    release="ubuntu"
  elif cat /etc/issue | grep -q -E -i "centos|red hat|redhat"
  then
    release="centos"
  elif cat /proc/version | grep -q -E -i "debian"
  then
    release="debian"
  elif cat /proc/version | grep -q -E -i "ubuntu"
  then
    release="ubuntu"
  elif cat /proc/version | grep -q -E -i "centos|red hat|redhat"
  then
    release="centos"
  fi
  if [[ "${release}" != "ubuntu" && "${release}" != "debian" && "${release}" != "centos" ]]
  then
    echo "很遗憾！本脚本暂时只支持Debian7+和Ubuntu12+和CentOS7+的系统！" && exit 1
  fi
}
# 安装依赖库和必要软件
Install_Dependency(){
  bit=`uname -m`
  if [[ "${release}" != "centos" ]]
  then
    if [[ "${bit}" = "x86_64" ]]
    then
      sudo dpkg --add-architecture i386
      sudo apt update
      sudo apt install -y lib32gcc1 libstdc++6 libstdc++6:i386 libcurl4-gnutls-dev:i386 libreadline-dev gcc make tmux wget openssl libssl-dev curl
    else
      sudo apt update
      sudo apt install -y libstdc++6 libcurl4-gnutls-dev tmux wget gcc make openssl libreadline-dev libssl-dev curl
    fi
  else
    if [[ "${bit}" = "x86_64" ]]
    then
      sudo yum install -y tmux glibc.i686 libstdc++ libstdc++.i686 libcurl.i686 wget gcc make openssl openssl-devel curl libtermcap-devel ncurses-devel libevent-devel readline-devel
    else
      sudo yum install -y wget tmux libstdc++ libcurl gcc make openssl openssl-devel curl libtermcap-devel ncurses-devel libevent-devel readline-devel
    fi
  fi
  lua -v > /dev/null 2>&1
  if [ $? -ne 0 ]
  then
      wget http://www.lua.org/ftp/lua-5.1.5.tar.gz -T 10
      tar -zxvf lua-5.1.5.tar.gz
      cd lua-5.1.5
      sudo make linux test
      sudo make install
      rm -rf ${install_path}/lua-5.1.5*
  fi
}
#安装
Install()
{

	echo '安装DST所需依赖库及软件 ...'
	#==================================================================
	#依赖安装开始
	cp -rf $install_path/icon.png $panel_static_path/ico-dst_manager.png
	
	Check_sys
	Install_Dependency > /dev/null 2>&1
	
	/www/server/panel/pyenv/bin/pip3 install lupa
	#依赖安装结束
	#==================================================================
	echo '================================================'
	echo '安装完成'
}

#卸载
Uninstall()
{
	rm -rf $install_path
	rm -rf $panel_static_path/ico-dst_manager.png
}

Update()
{
    down_url="https://tools.wqlin.com/dst/plugin"
    for file in $(ls $install_path|grep -v 'pycache')
    do
        url=${down_url}/$file
        wget -T 10 -q $url -O $install_path/$file
    done
}

#操作判断
if [ "${1}" == 'install' ];then
	Install
elif [ "${1}" == 'uninstall' ];then
	Uninstall
elif [ "${1}" == 'update' ];then
	Update
else
	echo 'Error!';
fi
