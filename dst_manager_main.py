#!/usr/bin/python
# coding: utf-8
# +-------------------------------------------------------------------
# | 宝塔Linux面板
# +-------------------------------------------------------------------
# | Copyright (c) 2015-2099 宝塔软件(http://bt.cn) All rights reserved.
# +-------------------------------------------------------------------
# | Author: 南风颂 <i@wqlin.com>
# +-------------------------------------------------------------------

# +-------------------------------------------------------------------
# | Steam平台饥荒联机版Linux独立服务器管理器
# +-------------------------------------------------------------------
import sys, os, json, re, time

# 设置运行目录
os.chdir("/www/server/panel")

# 添加包引用位置并引用公共包
sys.path.append("class/")
import public, files
from lupa import LuaRuntime


# 在非命令行模式下引用面板缓存和session对象
if __name__ != '__main__':
    from BTPanel import cache, session


class dst_manager_main:
    __plugin_path = "/www/server/panel/plugin/dst_manager"

    # 构造方法
    def __init__(self):
        # 服务器
        # self.dstserver_data_dir = "/www/server/panel/dst"
        self.dstserver_data_dir = os.path.join(self.__plugin_path, "data")
        self.dstcluster_dir = os.path.join(self.dstserver_data_dir, "cluster")
        self.dstconfig_dir = os.path.join(self.dstserver_data_dir, "config")
        self.dstlog_dir = os.path.join(self.dstserver_data_dir, "logs")
        if not os.path.isdir(self.dstserver_data_dir):
            public.ExecShell("mkdir -p {}".format(self.dstcluster_dir))
            public.ExecShell("mkdir -p {}".format(self.dstconfig_dir))
        self.server_info_path = os.path.join(self.dstserver_data_dir, "server_info.json")

        # 存档
        self.dst_dir = os.path.join(os.path.expanduser('~'), "DST")
        self.dst_cluster_dir = os.path.join(self.dst_dir, "Klei", "DoNotStarveTogether")
        self.dst_cluster_backup_dir = os.path.join(self.dst_dir, "Klei", "ClusterBackup")
        self.dst_log_backup_dir = os.path.join(self.dst_dir, "Klei", "LogBackup")
        self.dst_server_dir = os.path.join(self.dst_dir, "DSTServer")
        self.dst_mod_dir = os.path.join(self.dst_server_dir, "mods")
        if not os.path.isdir(self.dst_dir):
            public.ExecShell("mkdir -p {}".format(self.dst_cluster_dir))
            public.ExecShell("mkdir -p {}".format(self.dst_server_dir))
            public.ExecShell("mkdir -p {}".format(self.dst_cluster_backup_dir))
            public.ExecShell("mkdir -p {}".format(self.dst_log_backup_dir))
        
        self.hasLisence = self.checklisence()
    
    def checklisence(self):
        return True
        

    def create_cluster(self, args):
        if self.hasLisence:
            clusterid = args.clusterid
            cluster_dir = os.path.join(self.dst_cluster_dir, clusterid)
            if not os.path.exists(cluster_dir):
                public.ExecShell("mkdir -p {}".format(cluster_dir))
            sharddir = []
            for shard in os.listdir(os.path.join(self.dstcluster_dir, clusterid)):
                spath = os.path.join(self.dstcluster_dir, clusterid, shard)
                if os.path.isdir(spath):
                    sharddir.append(shard)
                    shard_path = os.path.join(cluster_dir, shard)
                    public.ExecShell("mkdir -p {}".format(shard_path))
            for shard in os.listdir(cluster_dir):
                spath = os.path.join(cluster_dir, shard)
                if os.path.isdir(spath):
                    if shard not in sharddir:
                        public.ExecShell("rm -rf {}".format(spath))
            # cluster.ini
            cluster_config_path = os.path.join(self.dstcluster_dir, clusterid, "cluster.json")
            if os.path.exists(cluster_config_path):
                cluster_data = self.read_json_data(cluster_config_path)
                if 'data' in cluster_data:
                    cluster_data_str = ""
                    cluster_nstr = '[NETWORK]'
                    cluster_gstr = '[GAMEPLAY]'
                    cluster_sstr = '[STEAM]'
                    cluster_ssstr = '[SHARD]'
                    cluster_mstr = '[MISC]'
                    for cluster_str in cluster_data['data']:
                        # if cluster_str['name'] == "master_port": ports.append(int(cluster_str['value']))
                        if cluster_str['type'] == '[NETWORK]':
                            cluster_nstr = cluster_nstr + '\n' + cluster_str['name']  + ' = ' + cluster_str['value']
                        if cluster_str['type'] == '[GAMEPLAY]':
                            cluster_gstr = cluster_gstr + '\n' + cluster_str['name']  + ' = ' + cluster_str['value']
                        if cluster_str['type'] == '[STEAM]':
                            cluster_sstr = cluster_sstr + '\n' + cluster_str['name']  + ' = ' + cluster_str['value']
                        if cluster_str['type'] == '[SHARD]':
                            cluster_ssstr = cluster_ssstr + '\n' + cluster_str['name']  + ' = ' + cluster_str['value']
                        if cluster_str['type'] == '[MISC]':
                            cluster_mstr = cluster_mstr + '\n' + cluster_str['name']  + ' = ' + cluster_str['value']
                    cluster_data_str = cluster_nstr + '\n\n' + cluster_gstr + '\n\n' + cluster_sstr + '\n\n' + cluster_ssstr + '\n\n' + cluster_mstr
                    cluster_file = os.path.join(cluster_dir, "cluster.ini")
                    with open(cluster_file, 'w', encoding="utf-8") as f:
                        f.write(cluster_data_str)
                else:
                    return {'data': '房间设置缺失，存档损坏！', "status": False}
            else:
                return {'data': '房间设置缺失，存档损坏！', "status": False}
            
            # token
            token = []
            tokenfile = os.path.join(self.dstserver_data_dir, "system.json")
            tflag = True
            if os.path.exists(tokenfile):
                token = self.read_json_data(tokenfile)
                token_str = token['token']
                if token_str != "":
                    token_file = os.path.join(cluster_dir, "cluster_token.txt")
                    tflag = False
                    with open(token_file, 'w', encoding="utf-8") as f:
                        f.write(token_str)
            if tflag: return {'data': '令牌缺失，请先设置令牌！', "status": False}
            
            # player list
            player_list_file = os.path.join(self.dstserver_data_dir, "player_list.json")
            if os.path.exists(player_list_file):
                players = self.read_json_data(player_list_file)
                adminstr = ""
                whitestr = ""
                blackstr = ""
                for player in players:
                    if player['admin'] == "true":
                        adminstr = adminstr + player['kleiID'] + "\n"
                    if player['black'] == "true":
                        blackstr = blackstr + player['kleiID'] + "\n"
                    if player['admin'] == "true":
                        whitestr = whitestr + player['kleiID'] + "\n"
                
                # 暂时兼容脚本，不知道还想做吗
                # admin_file = os.path.join(cluster_dir, "adminlist.txt")
                # with open(admin_file, 'w', encoding="utf-8") as f:
                #     f.write(adminstr) 
                # black_file = os.path.join(cluster_dir, "blocklist.txt")
                # with open(black_file, 'w', encoding="utf-8") as f:
                #     f.write(blackstr) 
                # white_file = os.path.join(cluster_dir, "whitelist.txt")
                # with open(white_file, 'w', encoding="utf-8") as f:
                #     f.write(whitestr)
                cluster_dir1 = os.path.join(self.dst_dir, "dstscript")
                admin_file = os.path.join(cluster_dir1, "alist.txt")
                with open(admin_file, 'w', encoding="utf-8") as f:
                    f.write(adminstr) 
                black_file = os.path.join(cluster_dir1, "blist.txt")
                with open(black_file, 'w', encoding="utf-8") as f:
                    f.write(blackstr) 
                white_file = os.path.join(cluster_dir1, "wlist.txt")
                with open(white_file, 'w', encoding="utf-8") as f:
                    f.write(whitestr) 
            # mod
            mod_config_path = os.path.join(self.dstcluster_dir, clusterid, "mod.json")
            if os.path.exists(mod_config_path):
                mod_data = self.read_json_data(mod_config_path)
                mod_data = {k:v for k,v in mod_data.items() if 'enabled' in v and v['enabled'] == "true"}
                modstr = "return {"
                mindex = 0
                for key,mod in mod_data.items():
                    if 'enabled' in mod and mod['enabled'] == "true":
                        modstr = modstr + '\n' + '  ["' + key + '"]={' 
                        modstr = modstr + '\n' + '    ["enabled"]=true'
                        if 'configuration_options' in mod:
                            modstr = modstr + ','
                            modstr = modstr + '\n' + '    ["configuration_options"]={'
                            index = 0
                            modc = mod['configuration_options']
                            for ckey,cmod in modc.items():
                                cmodstr = cmod
                                isbool = True
                                isnum = True
                                if cmodstr != "true" and cmodstr != "false":
                                    isbool = False
                                try:
                                    cmodstr = float(cmodstr)
                                except:
                                    isnum = False
                                if isnum or isbool:
                                    modstr = modstr + '\n' + '      ["' + ckey + '"]='+ cmod
                                else:
                                    modstr = modstr + '\n' + '      ["' + ckey + '"]="'+ cmod + '"'
                                index = index + 1
                                if index < len(modc):
                                    modstr = modstr + ','
                            
                            modstr = modstr + '\n' + '    }'
                        modstr = modstr + '\n' + '  }'
                        mindex = mindex + 1
                        if mindex < len(mod_data):
                            modstr = modstr + ','
                modstr = modstr + '\n' + '}'
                for shard in os.listdir(cluster_dir):
                    sspath = os.path.join(cluster_dir, shard)
                    if os.path.isdir(sspath):
                        shard_mod_file = os.path.join(cluster_dir, shard, "modoverrides.lua")
                        with open(shard_mod_file, 'w', encoding="utf-8") as f:
                            f.write(modstr)
            # server.ini
            shardnum = 0
            shardarr = []
            for shard in os.listdir(cluster_dir):
                sspath = os.path.join(self.dstcluster_dir, clusterid, shard)
                if os.path.isdir(sspath):
                    shard_config_path = os.path.join(sspath, "shard.json")
                    shardtype = ""
                    shardnum = shardnum + 1
                    shardarr.append(shard)
                    if os.path.exists(shard_config_path):
                        shard_data = self.read_json_data(shard_config_path)
                        shard_data_str = ""
                        shard_nstr = '[NETWORK]'
                        shard_sstr = '[STEAM]'
                        shard_ssstr = '[SHARD]'
                        shard_mstr = '[ACCOUNT]'
                        for shard_str in shard_data:
                            # if "port" in shard_str['name']: ports.append(int(shard_str['value']))
                            if shard_str['name'] == "shard_type": shard_type = shard_str['value']
                            if shard_str['name'] == "shardname": shard_str['name'] = "name"
                            if shard_str['type'] == '[NETWORK]':
                                shard_nstr = shard_nstr + '\n' + shard_str['name']  + ' = ' + shard_str['value']
                            if shard_str['type'] == '[STEAM]':
                                shard_sstr = shard_sstr + '\n' + shard_str['name']  + ' = ' + shard_str['value']
                            if shard_str['type'] == '[SHARD]':
                                shard_ssstr = shard_ssstr + '\n' + shard_str['name']  + ' = ' + shard_str['value']
                            if shard_str['type'] == '[ACCOUNT]':
                                shard_mstr = shard_mstr + '\n' + shard_str['name']  + ' = ' + shard_str['value']
                        shard_data_str = shard_nstr + '\n\n' + shard_sstr + '\n\n' + shard_ssstr + '\n\n' + shard_mstr
                        shard_file = os.path.join(cluster_dir, shard, "server.ini")
                        with open(shard_file, 'w', encoding="utf-8") as f:
                            f.write(shard_data_str)
                    else:
                        return {'data': '世界设置缺失，存档损坏！', "status": False}
                    
                    # leveldata
                    if shard_type == "forest" or shard_type == "caves":
                        shard_level_data_file = os.path.join(sspath, shard_type+"leveldata.json")
                        if not os.path.exists(shard_level_data_file):
                            shard_level_data_file = os.path.join(self.dstconfig_dir, shard_type+"leveldata.json")
                        level_data = self.read_json_data(shard_level_data_file)
                        level_data_str = 'return {'
                        for lkey,leveld in level_data.items():
                            if lkey != 'overrides':
                                if '{' in leveld:
                                    level_data_str = level_data_str + '\n' + '  ["' + lkey + '"]=' + leveld + ','
                                else:
                                    level_data_str = level_data_str + '\n' + '  ["' + lkey + '"]="' + leveld + '",'
                        overrides_data = level_data['overrides']
                        level_data_str = level_data_str + '\n' + '  ["overrides"]={'
                        oindex = 0 
                        for leveloo in overrides_data:
                            if leveloo['type'] != "shardtype" and leveloo['type'] != "clusterid" and leveloo['type'] != "shardid":
                                level_data_str = level_data_str + '\n' + '    ["' + leveloo['name'] + '"]="' + leveloo['value'] + '"'
                                oindex = oindex + 1
                            if oindex < len(overrides_data)-3 :
                                level_data_str = level_data_str + ','
                        level_data_str = level_data_str + '\n  }\n}'
                        level_file = os.path.join(cluster_dir, shard, "leveldataoverride.lua")
                        with open(level_file, 'w', encoding="utf-8") as f:
                            f.write(level_data_str)
                    else:
                        cmdstr = 'cp -f ' + os.path.join(self.dstconfig_dir, shard_type + '.lua ') + os.path.join(cluster_dir, shard, "leveldataoverride.lua")
                        public.ExecShell(cmdstr)
            if shardnum < 1: return {'data': '没有添加世界，存档损坏！', "status": False}
            # cmdstr = 'nohup bash ' + os.path.join(self.__plugin_path, "run.sh") + ' "' + clusterid + '" ' + '"' + " ".join(shardarr) + '" > ' + os.path.join(self.dstconfig_dir, "dst.log") + ' 2>&1 &'
            # public.ExecShell(cmdstr)
            # return {'data': {"clusterid":clusterid,"shardarr":" ".join(shardarr)}, "status": True}
            return {"data": "存档配置生成完毕！", "status": True}
        else:
            return {"data": "没有授权！", "status": False}
    
    def save_cluster_data(self, args): # 保存房间设置
        if self.hasLisence:
            cluster_id = args.cluster_id
            cluster_config_path = os.path.join(self.dstcluster_dir, cluster_id, "cluster.json")
            olddata = self.read_json_data(cluster_config_path)
            olddata['info'][0]['cluster_name'] = args.cluster_name
    
            if 'data' not in olddata:
                cluster_data_path = os.path.join(self.dstconfig_dir, "clusterdata.json")
                olddata['data'] = self.read_json_data(cluster_data_path)
            for k in olddata['data']:
                if k['name'] in args:
                    k['value'] = args[k['name']]
    
            self.write_json_data(cluster_config_path, olddata, mode='w')
    
            # 返回数据到前端
            return {'data': '房间设置保存成功！', "status": True}
        else:
            return {"data": "没有授权！", "status": False}
    
    def update_plugin(self, args):
        if self.hasLisence:
            public.ExecShell("bash {}/install.sh update".format(self.__plugin_path))
            return {'data': '更新成功！', "status": True}
        else:
            return {"data": "没有授权！", "status": False}
            
    def get_sys_setting(self, args):
        data = []
        tokenfile = os.path.join(self.dstserver_data_dir, "system.json")
        if os.path.exists(tokenfile):
            data = self.read_json_data(tokenfile)
            
        import requests
        url = 'https://tools.wqlin.com/dst/dst.php?type=version'
        resp = requests.get(url)
        if resp.status_code == requests.codes.ok:
            v = json.loads(resp.text)
            data['newversion'] = v['release']
            
        url1 = 'https://tools.wqlin.com/dst/plugin/version.txt'
        resp1 = requests.get(url1)
        if resp1.status_code == requests.codes.ok:
            data['newpluginversion'] = resp1.text.strip()
        cur_vf1 = os.path.join(self.__plugin_path, "version.txt")
        if os.path.exists(cur_vf1):
            with open(cur_vf1, 'r', encoding="utf-8") as f:
                data['curpluginversion'] = f.read().strip()
                
        # lic_vf = os.path.join(self.dstserver_data_dir, "lisence.lic")
        # if os.path.exists(lic_vf):
        #     with open(lic_vf, 'r', encoding="utf-8") as f:
        #         data['lic'] = f.read().strip()
                
        cur_vf = os.path.join(self.dst_server_dir, "version.txt")
        if os.path.exists(cur_vf):
            with open(cur_vf, 'r', encoding="utf-8") as f:
                data['curversion'] = f.read().strip()
        else:
            data['curversion'] = ''
        if not self.hasLisence:
            data['lisence'] = "false"
        else:
            data['lisence'] = "true"
        return {'data': data, "status": True}
        
    def get_mod_path(self, args):
        if self.hasLisence:
            data = self.dst_mod_dir
            return {'data': data, "status": True}
        else:
            return {"data": "没有授权！", "status": False}
    def set_sys_setting(self, args):
        tokenfile = os.path.join(self.dstserver_data_dir, "system.json")
        data = self.read_json_data(tokenfile)
        checklic = False
        for key in data:
            if key in args:
                data[key] = args[key]
            self.write_json_data(tokenfile, data, mode='w')
        return {'data': "设置保存成功！", "status": True}

    def server_update(self, args):
        if self.hasLisence:
            if os.path.exists(os.path.join(self.dstlog_dir, "running")):
                return {'data': "请等待上一操作执行完毕", "status": False}
            else:
                cmdstr = 'bash ' + os.path.join(self.__plugin_path, "dst.sh") + ' ' + self.dstlog_dir + ' ' + args.t
                public.ExecShell(cmdstr)
                return {'data': "操作执行成功！", "status": True}
        else:
            return {"data": "没有授权！", "status": False}
    def get_server_log(self, args):
        if self.hasLisence:
            file = os.path.join(self.dstlog_dir, args.t+'.log')
            result = public.ExecShell("tail -50 {}".format(file))[0]
            # 返回数据到前端
            return {'data': result, "status": True}
        else:
            return {"data": "没有授权！", "status": False}
    # 写入json
    def write_json_data(self, file, data, mode):
        with open(file, mode, encoding="utf-8") as f:
            f.write(json.dumps(data, ensure_ascii=False))

    # 读取json
    def read_json_data(self, file):
        with open(file, 'r', encoding="utf-8") as f:
            return json.load(f)
    def get_player_list(self, args):
        if self.hasLisence:
            player_list_file = os.path.join(self.dstserver_data_dir, "player_list.json")
            data = []
            if os.path.isfile(player_list_file):
                data = self.read_json_data(player_list_file)
    
            # 返回数据到前端
            return {'data': data, "status": True}
        else:
            return {"data": "没有授权！", "status": False}
    def get_server_list(self, args):  # 获取服务器列表
        if self.hasLisence:
            server_info_path = self.server_info_path
            data = []
            if os.path.isfile(server_info_path):
                data = self.read_json_data(server_info_path)
    
            # 返回数据到前端
            return {'data': data, "status": True}
        else:
            return {"data": "没有授权！", "status": False}
    def get_cluster_list(self, args): # 获取存档列表
        if self.hasLisence:
            cluster_dir = self.dstcluster_dir
            data = []
            for item in os.listdir(cluster_dir):
                cluster_info_path = os.path.join(cluster_dir, item, "cluster.json")
                cluster_data = self.read_json_data(cluster_info_path)
                cluster_data = cluster_data['info'][0]
                cdata = {}
                cdata["cluster_name"] = cluster_data["cluster_name"]
                cdata["cluster_create_time"] = cluster_data["cluster_create_time"]
                cdata["cluster_folder"] = cluster_data["cluster_folder"]
                cdata["cluster_path"] = os.path.join(self.dst_cluster_dir, cluster_data["cluster_folder"])
                data.append(cdata)
            # 返回数据到前端
            return {'data': data, "status": True}
        else:
            return {"data": "没有授权！", "status": False}
    def get_shard_list(self, args): # 获取世界列表
        if self.hasLisence:
            cluster_dir = self.dstcluster_dir
            clusterid = args.id
            cluster_dir_path = os.path.join(cluster_dir, clusterid)
            data = []
            for item in os.listdir(cluster_dir_path):
                if os.path.isdir(os.path.join(cluster_dir_path, item)):
                    shard_info_path = os.path.join(cluster_dir_path, item, "shard.json")
                    shard_data = self.read_json_data(shard_info_path)
                    data.append(shard_data)
            
            # 返回数据到前端
            return {'data': data, "status": True}
        else:
            return {"data": "没有授权！", "status": False}
    def del_mod(self, args):
        if self.hasLisence:
            moddir = args.moddir
            root = self.dst_mod_dir
            if os.path.exists(os.path.join(root, moddir)):
                public.ExecShell("rm -rf {}".format(os.path.join(root, moddir)))
                
            return {'data': "删除成功！", "status": True}
        else:
            return {"data": "没有授权！", "status": False}
    def switch_mod_status(self, args):
        if self.hasLisence:
            moddir = args.moddir
            clusterid = args.clusterid
            data = {}
            mod_config_path = os.path.join(self.dstcluster_dir, clusterid, "mod.json")
            if os.path.exists(mod_config_path):
                data = self.read_json_data(mod_config_path)
            if moddir not in data:
                data[moddir] = {}
            data[moddir]['enabled'] = args.used
            self.write_json_data(mod_config_path, data, mode='w')
            msg = "禁用成功！"
            if args.used:
                msg = "启用成功！"
            return {'data': msg, "status": True}
        else:
            return {"data": "没有授权！", "status": False}
    # 取出MOD基本信息
    def getModInfo(self, moddir, t="all"):
        modinfo = {}
        root = self.dst_mod_dir
        olddir = os.getcwd()
        os.chdir(root)
        if not os.path.exists(os.path.join(root, "json.lua")):
            public.ExecShell("cp -f " + os.path.join(self.dstserver_data_dir, "json.lua") + os.path.join(root, "json.lua"))
        
        if os.path.exists(os.path.join(root, moddir, "modinfo.lua")):
            lua = LuaRuntime(unpack_returned_tuples=True)
            lua.require(os.path.join(moddir, "modinfo"))
            if os.path.exists(os.path.join(root, moddir, "modinfo_chs.lua")):
                lua.require(os.path.join(moddir, "modinfo_chs"))
            modinfo["name"] = lua.eval('name').strip()
            modinfo["moddir"] = moddir
            t1 = lua.eval('server_only_mod')
            t3 = lua.eval('all_clients_require_mod')
            t2 = lua.eval('client_only_mod')
            modinfo['load_type'] = "服务端"
            if t1:
                modinfo['load_type'] = "服务端"
            if t2:
                modinfo['load_type'] = "客户端"
            if t3:
                modinfo['load_type'] = "所有人"
            modinfo["author"] = lua.eval('author').strip()
            modinfo["version"] = lua.eval('version').strip()
            lua.require("json")
            config_json_str = lua.eval('encode_compliant(configuration_options)')
            modinfo["configuration_options"] = json.loads(config_json_str)
            if modinfo["configuration_options"]:
                modinfo['configable'] = True
            else:
                modinfo['configable'] = False
            if t == "basic":
                modinfo["configuration_options"] = []
            else:
                modinfo["description"] = lua.eval('description').strip()
                modinfo["server_only_mod"] = lua.eval('server_only_mod')
                modinfo["all_clients_require_mod"] = lua.eval('all_clients_require_mod')
                modinfo["client_only_mod"] = lua.eval('client_only_mod')

        os.chdir(olddir)
        return modinfo
    
    def get_all_mod_list(self, args):  #获取所有已安装的MOD列表
        if self.hasLisence:
            mod_root = self.dst_mod_dir
            clusterid = args.clusterid
            mod_config_path = os.path.join(self.dstcluster_dir, clusterid, "mod.json")
            moddata = []
            if os.path.exists(mod_config_path):
                moddata = self.read_json_data(mod_config_path)
            data = []
            for moddir in os.listdir(mod_root):
                modpath = os.path.join(mod_root, moddir)
                if os.path.isdir(modpath):
                    if os.path.exists(os.path.join(mod_root, moddir, "modinfo.lua")):
                        info = self.getModInfo(moddir, "basic")
                        info['enabled'] = False
                        if moddata and moddir in moddata:
                            if 'enabled' in moddata[moddir]:
                                info['enabled'] = moddata[moddir]['enabled']
                        info['path'] = modpath
                        data.append(info)
            
            # 返回数据到前端
            return {'data': data, "status": True}
        else:
            return {"data": "没有授权！", "status": False}
    def get_mod_config(self, args):  #获取所有已安装的MOD列表
        if self.hasLisence:
            mod_root = self.dst_mod_dir
            clusterid = args.clusterid
            moddir = args.moddir
            modopdata = self.getModInfo(moddir)
            modop = modopdata["configuration_options"]
            mod_config_path = os.path.join(self.dstcluster_dir, clusterid, "mod.json")
            oldmodop = []
            needold = True
            if os.path.exists(mod_config_path):
                oldmodop = self.read_json_data(mod_config_path)
            if moddir in oldmodop:
                if "configuration_options" in oldmodop[moddir]:
                    t = oldmodop[moddir]["configuration_options"]
                    needold = False
                    for op in modop:
                        if op['name'] in t:
                            op['default'] = t[op['name']]
            if needold:
                oldmodconfig_file = os.path.join(self.dstconfig_dir, "modconfig", moddir+".json")
                if os.path.exists(oldmodconfig_file):
                    t = self.read_json_data(oldmodconfig_file)
                    for op in modop:
                        if op['name'] in t:
                            op['default'] = t[op['name']]
                
            # 返回数据到前端
            return {'data': modop, "status": True}
        else:
            return {"data": "没有授权！", "status": False}
    def set_mod_config(self, args):  #获取所有已安装的MOD列表
        if self.hasLisence:
            mod_root = self.dst_mod_dir
            clusterid = args.clusterid
            moddir = args.moddir
            mod_config_path = os.path.join(self.dstcluster_dir, clusterid, "mod.json")
            oldmodop = {}
            if os.path.exists(mod_config_path):
                oldmodop = self.read_json_data(mod_config_path)
            if moddir not in oldmodop:
                oldmodop[moddir] = {}
            modopdata = self.getModInfo(moddir)
            modop = modopdata["configuration_options"]
            if "configuration_options" not in oldmodop[moddir]:
                oldmodop[moddir]["configuration_options"] = {}
            for k in modop:
                if k['name'] in args:
                    key = k['name']
                    if args[key]:
                        oldmodop[moddir]["configuration_options"][key] = args[key]
            self.write_json_data(mod_config_path, oldmodop, mode='w')
            oldmodconfig_file = os.path.join(self.dstconfig_dir, "modconfig", moddir+".json")
            self.write_json_data(oldmodconfig_file, oldmodop[moddir]["configuration_options"], mode='w')
            # 返回数据到前端
            return {'data': "MOD配置保存完成！", "status": True}
        else:
            return {"data": "没有授权！", "status": False}
    def del_player_list(self, args):
        if self.hasLisence:
            player_list_file = os.path.join(self.dstserver_data_dir, "player_list.json")
            data = []
            newdata = []
            if os.path.isfile(player_list_file):
                data = self.read_json_data(player_list_file)
            
            for player in data:
                if player['kleiID'] != args['kleiID']:
                    newdata.append(player)
            
            self.write_json_data(player_list_file, newdata, mode='w')
    
            # 返回数据到前端
            return {'data': "删除成功！", "status": True}
        else:
            return {"data": "没有授权！", "status": False}
    def edit_player_list(self, args):
        if self.hasLisence:
            player_list_file = os.path.join(self.dstserver_data_dir, "player_list.json")
            data = []
            if os.path.isfile(player_list_file):
                data = self.read_json_data(player_list_file)
            
            isexist = False
            for player in data:
                if player['kleiID'] == args['kleiID']:
                    player['steamid'] = args['steamid']
                    player['nickname'] = args['nickname']
                    player['black'] = args['black']
                    player['white'] = args['white']
                    player['admin'] = args['admin']
                    player['origin'] = args['origin']
                    
                    isexist = True
                    
            if not isexist:
                player = {"kleiID":args['kleiID'], "steamid": args['steamid'], "nickname": args['nickname'], "black": args['black'], "white": args['white'], "admin": args['admin'], "origin": args['origin']}
                data.append(player)
            
            self.write_json_data(player_list_file, data, mode='w')
    
            # 返回数据到前端
            return {'data': "修改成功！", "status": True}
        else:
            return {"data": "没有授权！", "status": False}
    def edit_server(self, args):  #
        if self.hasLisence:
            op_type = args.type
            server_info_path = self.server_info_path
            if op_type == "add":
                dst_ip = args.ip
                if dst_ip.strip() in ["'127.0.0.1'", "'localhost'"]:
                    return {'data': "本地服务器不用添加，添加失败！", "status": False}
                data = []
                if os.path.isfile(server_info_path):
                    data = self.read_json_data(server_info_path)
                    for list in data:
                        if list['ip'] == args.ip:
                            return {'data': "服务器已经存在", "status": False}
                server_info = {"dstserver": args.dstserver, "username": args.username, "password": args.password, "ip": dst_ip, "port": args.port}
                data.append(server_info)
                self.write_json_data(server_info_path, data, mode='w')
    
                # 返回数据到前端
                return {'data': "服务器添加成功", "status": True}
            else:
                username = args.username
                password = args.password
                dstserver = args.dstserver
                port = args.port
                ip = args.ip
                server_info_str = ''
                if os.path.isfile(server_info_path):
                    data = self.read_json_data(server_info_path)
                    for item in data:
                        if item['ip'] == ip:
                            item['password'] = password
                            item['dstserver'] = dstserver
                            item['username'] = username
                            item['port'] = port
                            break
                self.write_json_data(server_info_path, data, mode='w')
    
                # 返回数据到前端
                return {'data': "服务器信息修改成功", "status": True}
        else:
            return {"data": "没有授权！", "status": False}
    def edit_shard(self, args):  # 添加或修改世界
        if self.hasLisence:
            clustershardid = args.clustershardid
            shardfolder = args.shardfolder
            shard_dir_path = os.path.join(self.dstcluster_dir, clustershardid, shardfolder)
            if not os.path.exists(shard_dir_path):
                public.ExecShell("mkdir -p {}".format(shard_dir_path))
            shard_info_path = os.path.join(shard_dir_path, "shard.json")
            if not os.path.exists(shard_info_path):
                olddata = self.read_json_data(os.path.join(self.dstconfig_dir, "sharddata.json"))
            else:
                olddata = self.read_json_data(shard_info_path)
            for k in olddata:
                if k['name'] in args:
                    k['value'] = args[k['name']]
            
            self.write_json_data(shard_info_path, olddata, mode='w')
    
            # 返回数据到前端
            return {'data': "服务器信息修改成功", "status": True}
        else:
            return {"data": "没有授权！", "status": False}
    def download_dst_cluster(self, args): # 下载存档
        if self.hasLisence:
            clusterid = args.clusterid
            zip_path = os.path.join(self.dst_cluster_backup_dir, clusterid + ".zip")
            public.ExecShell("rm -rf {}/*.zip".format(self.dst_cluster_backup_dir))
            public.ExecShell("cd {} && zip -q -r {} {}".format(self.dst_cluster_dir, zip_path, clusterid))
            return {'data': zip_path, "status": True}
        else:
            return {"data": "没有授权！", "status": False}
    def del_dst_server(self, args):  # 删除数据库
        if self.hasLisence:
            ip = args.ip
            if ip == "127.0.0.1":
                return {'data': "删除服务器失败， 本地服务器不可删除！", "status": False}
            server_info_path = self.server_info_path
            newdata = []
            if os.path.isfile(server_info_path):
                data = self.read_json_data(server_info_path)
                for slist in data:
                    if slist['ip'] != ip:
                        newdata.append(slist)
            self.write_json_data(server_info_path, newdata, mode='w')
    
            # 返回数据到前端
            return {'data': "删除服务器成功", "status": True}
        else:
            return {"data": "没有授权！", "status": False}
    def get_cluster_data(self, args): # 返回房间设置数据
        if self.hasLisence:
            clusterid = args.id
            data = []
            cluster_info_path = os.path.join(self.dstcluster_dir, clusterid, "cluster.json")
            data1 = self.read_json_data(cluster_info_path)
            if 'data' in data1.keys():
                data = data1['data']
            else:
                cluster_data_path = os.path.join(self.dstconfig_dir, "clusterdata.json")
                data = self.read_json_data(cluster_data_path)
            # 返回数据到前端
            return {'data': data, "status": True}
        else:
            return {"data": "没有授权！", "status": False}
    def get_shard_data(self, args): # 返回世界设置数据
        if self.hasLisence:
            clusterid = args.clusterid
            shardid = args.shardid
            data = []
            ro = True
            if shardid != "":
                shard_info_path = os.path.join(self.dstcluster_dir, clusterid, shardid, "shard.json")
                data = self.read_json_data(shard_info_path)
                ro = False
            if ro:
                shard_data_path = os.path.join(self.dstconfig_dir, "sharddata.json")
                data = self.read_json_data(shard_data_path)
            # 返回数据到前端
            return {'data': data, "status": True}
        else:
            return {"data": "没有授权！", "status": False}
    def get_shard_env_data(self, args): # 返回世界环境设置数据
        if self.hasLisence:
            clusterid = args.clusterid
            shardid = args.shardid
            shardtype = args.shardtype.strip()
            filename = ""
            if shardtype == "地面":
                filename = "forestleveldata.json"
            if shardtype == "洞穴":
                filename = "cavesleveldata.json"
    
            shard_level_path = os.path.join(self.dstcluster_dir, clusterid, shardid, filename)
            
            data = []
            if os.path.exists(shard_level_path):
                data = self.read_json_data(shard_level_path)
            else:
                data = self.read_json_data(os.path.join(self.dstconfig_dir, filename))
                
            # 返回数据到前端
            return {'data': data, "status": True}
        else:
            return {"data": "没有授权！", "status": False}
    def save_shard_env_data(self, args): # 保存世界环境设置数据
        if self.hasLisence:
            clusterid = args.clusterid
            shardid = args.shardid
            shardtype = args.shardtype.strip()
            filename = ""
            if shardtype == "地面":
                filename = "forestleveldata.json"
            if shardtype == "洞穴":
                filename = "cavesleveldata.json"
    
            shard_level_path = os.path.join(self.dstcluster_dir, clusterid, shardid, filename)
            data = []
            if os.path.exists(shard_level_path):
                data = self.read_json_data(shard_level_path)
            else:
                data = self.read_json_data(os.path.join(self.dstconfig_dir, filename))
            for k in data['overrides']:
                if k['name'] in args:
                    k['value'] = args[k['name']].strip()
            self.write_json_data(shard_level_path, data, mode='w')
                
            # 返回数据到前端
            return {'data': "环境设置保存成功！", "status": True}
        else:
            return {"data": "没有授权！", "status": False}
    def del_dst_shard(self, args): # 删除世界
        if self.hasLisence:
            clusterid = args.clusterid
            shardid = args.shardid
            if clusterid != "" and shardid != "":
                dst_shard_dir = os.path.join(self.dstcluster_dir, clusterid, shardid)
                public.ExecShell("rm -rf {}".format(dst_shard_dir))
    
            # 返回数据到前端
            return {'data': "删除世界成功!", "status": True}
        else:
            return {"data": "没有授权！", "status": False}
    
    def del_dst_cluster(self, args): # 删除存档
        if self.hasLisence:
            clusterid = args.clusterid
            del_cluster_bak = args.del_cluster_bak
            if int(del_cluster_bak) == 1:
                pass
            if clusterid != "":
                dstcluster_dir = os.path.join(self.dstcluster_dir, clusterid)
                dst_cluster_dir = os.path.join(self.dst_cluster_dir, clusterid)
    
                public.ExecShell("rm -rf {}".format(dstcluster_dir))
                public.ExecShell("rm -rf {}".format(dst_cluster_dir))
    
            # 返回数据到前端
            return {'data': "删除存档成功!", "status": True}
        else:
            return {"data": "没有授权！", "status": False}
    def get_current_time(self):
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    def add_dstcluster(self, args):  # 新建存档
        if self.hasLisence:
            folder = args.clusterfolder
            name = "新建存档" + folder
            time = self.get_current_time()
            cluster_path = os.path.join(self.dstcluster_dir, folder)
            if not os.path.exists(cluster_path):
                public.ExecShell("mkdir -p {}".format(cluster_path))
    
            cluster_info_path = os.path.join(cluster_path, "cluster.json")
            cluster_info = {}
            cluster_info["cluster_name"] = name
            cluster_info["cluster_folder"] = folder
            cluster_info["cluster_create_time"] = time
            clusters = {}
            clusters['info'] = []
            clusters['info'].append(cluster_info)
            self.write_json_data(cluster_info_path, clusters, mode='a')
    
            # 返回数据到前端
            return {'data': "存档新建成功, 可以修改设置了！", "status": True}
        else:
            return {"data": "没有授权！", "status": False}