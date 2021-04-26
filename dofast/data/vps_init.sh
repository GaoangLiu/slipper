#!/user/bin/env bash 

# check system distribution and return corresponding package installing method 
pack_meth(){
    local systemPackage=''

    if [[ -f /etc/redhat-release ]]; then
        systemPackage="yum"
    elif grep -Eqis "debian|raspbian" /etc/issue; then
        systemPackage="apt"
    elif grep -Eqis "ubuntu" /etc/issue; then
        systemPackage="apt"
    elif grep -Eqis "centos|red hat|redhat" /etc/issue; then
        systemPackage="yum"
    elif grep -Eqis "debian|raspbian" /proc/version; then
        systemPackage="apt"
    elif grep -Eqis "ubuntu" /proc/version; then
        systemPackage="apt"
    elif grep -Eqis "centos|red hat|redhat" /proc/version; then
        systemPackage="yum"
    else
        systemPackage="unknown"
    fi
    echo $systemPackage
}

PACKMETHOD=$(pack_meth)

install_libs() {
	$PACKMETHOD install -y python3-pip tree zip python3-pip emacs bmon vnstat ufw 
    $PACKMETHOD install -y aria2 jq htop shadowsocks-libev 
    snap install gost
}

# For monitoring [Data, CPU, Network-speed] usage
stat_lib() {
	$PACKMETHOD install -y vnstat iftop bmon tcptrack slurm speedtest-cli sysstat bc pv
}

# regular used softwares
regular_lib() {
	$PACKMETHOD install -y nautilus-dropbox nginx-full tree expect npm 
}

# update system before installing softwares, this script has to be executed by root 
update_sys() {
	if [ "$PACKMETHOD" == "unknown" ]; then 
		echo "**Your system is not supported"
		exit
	fi

	echo -n "**Check for root: "
	if [ "$EUID" -ne 0 ]
	then
		echo -e "[\033[1;31m ✘\033[0m ]"
		echo "**Please run as root. "
		exit 
	else
		echo -e "[\033[1;32m ✔\033[0m ]"
		$PACKMETHOD update && $PACKMETHOD upgrade -y 		
	fi
    echo "
alias p9='ping -W500 -i0.2 -c9'
alias mp='ping -W500 -i0.2 -c'
alias flushbash='source ~/.bashrc'
" >> ~/.bashrc 

	source ~/.bashrc
}

ufw_config() {
    sudo ufw allow ssh
    echo "y" | sudo ufw enable
}

# ============================================== CONFIGURATIONS
update_sys
install_libs
ufw_config


