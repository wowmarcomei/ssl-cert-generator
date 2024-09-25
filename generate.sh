#!/bin/bash

# 默认值
COUNTRY_NAME=CN
ORG_NAME=Myweb
OU_NAME="Myweb Application"
CN_ROOT=Application
CN_SUB=his-erp-lingqu.Mywebcloud.com
PASSWD=changeit
DURATION_DAYS=18250


#根证书文件，当客户提供证书文件时，也会通过输入参数被这两个变量捕获
ROOT_CRT=root.crt
ROOT_KEY=root.key

#输出文件
SUB_CRT="his-ssl-cert.crt"
SUB_KEY="his-ssl-cert.key"
JAVA_KEYSTORE='his-server-keystore.pfx'
JAVA_TRUSTSTORE='his-cacerts.jks'


# 创建根证书的配置文件
cat > root.cnf <<EOF
[ req ]
distinguished_name = req_distinguished_name
x509_extensions = v3_ca
prompt = no

[ req_distinguished_name ]
C = $COUNTRY_NAME
O = $ORG_NAME
OU = $OU_NAME
CN = $CN_ROOT

[ v3_ca ]
basicConstraints = CA:TRUE
keyUsage = digitalSignature, keyCertSign, cRLSign
EOF

# 创建子证书的配置文件
cat > sub.cnf <<EOF
[ CA_default ]
certificate = $ROOT_CRT
private_key = $ROOT_KEY

[ req ]
distinguished_name = req_distinguished_name
x509_extensions = v3_sub
prompt = no

[ req_distinguished_name ]
C = $COUNTRY_NAME
O = $ORG_NAME
OU = $OU_NAME
CN = *.$CN_SUB

[ v3_sub ]
basicConstraints = CA:FALSE
keyUsage = nonRepudiation, digitalSignature, keyEncipherment, dataEncipherment, keyAgreement
extendedKeyUsage = serverAuth, clientAuth
subjectAltName = @alt_names

[ alt_names ]
DNS.1 = *.$CN_SUB
DNS.2 = *.datafabric.svc.cluster.local
DNS.3 = *.headless-datafabric.datafabric.svc.cluster.local
DNS.4 = *.datafabric
DNS.5 = *.headless-datafabric.datafabric
DNS.6 = *.tenant-eureka.his-iam.svc.cluster.local
DNS.7 = *.gaia
DNS.8 = *.gaia-log
DNS.9 = *.gaia-monitoring
DNS.10 = *.his-iam
DNS.11 = *.his-observe
DNS.12 = *.jalor
DNS.13 = *.liveflow
DNS.14 = *.livefunction
DNS.15 = *.liveconnector
DNS.16 = *.monitoring
DNS.17 = *.starling
DNS.18 = *.flashsync
DNS.19 = *.csb
DNS.20 = *.edm
DNS.21 = *.bds
EOF

#生成证书函数
generate_certificate() {
    local command=$1
    local errorMessage=$2
    local successMessage=$3
    echo "---------------------------------------------------"

    if ! $command; then
        echo $errorMessage
        exit 1
    else
        echo $successMessage
    fi
}

# 生成随机名称的函数
generate_random_name() {
  # 使用 openssl rand 生成随机字节序列,生成 8 个随机字节，并以十六进制格式输出。
  local random_bytes=$(openssl rand -hex 8)
  # 将字节序列转换为字符串，并将其作为函数的返回值
  echo "alias_$random_bytes"
}

# 文件清理函数
clean_files() {
  local files=("$@")
  for file in "${files[@]}"; do
    if [ -e "$file" ]; then
      rm -f "$file"
      echo "清理文件: $file"
    fi
  done
}

# 生成 Keystore 文件的函数
generate_keystore() {
  local sub_crt=$1
  local sub_key=$2
  local keystore_file=$3
  local alias_name=$4
  local keystore_password=$5

  echo "---------------------------------------------------"
  echo "Generate Keystore file for java applications according to ($sub_crt) and ($sub_key) ..."
  openssl pkcs12 -export -in $sub_crt -inkey $sub_key -out $keystore_file -name $alias_name -passout pass:$keystore_password
  if [ $? -ne 0 ]; then
    echo "Failed to generate Keystore file."
    exit 1
  fi
  echo "Successfully generate Keystore file ($keystore_file) with alias name: $alias_name password: $keystore_password"
}

# 生成 Truststore 文件的函数
generate_truststore() {
  local alias_name=$1
  local root_crt=$2
  local truststore_file=$3
  local truststore_password=$4

  echo "---------------------------------------------------"
  echo "Generate Truststore file for java applications according to ($root_crt) ..."
  keytool -import -alias $alias_name -file $root_crt -keystore $truststore_file -storepass $truststore_password -noprompt
  if [ $? -ne 0 ]; then
    echo "Failed to generate Truststore file."
    exit 1
  fi
  echo "Successfully generate Truststore file ($truststore_file) with alias name: $alias_name and password: $truststore_password"
}

if ! command -v openssl &> /dev/null;then
    echo "OpenSSL could not be found. Please install it and try again."
    exit 1
else
    echo "OpenSSL version information: $(openssl version)"
    # 检查 OpenSSL 版本
    OPENSSL_VERSION=$(openssl version | cut -d' ' -f2)
    MAJOR_VERSION=$(echo $OPENSSL_VERSION | cut -d'.' -f1)
    if (( MAJOR_VERSION >= 3 )); then
        echo "OpenSSL version 3 or above is not supported. Please use OpenSSL version 1.x (e.g., 1.1.1)."
        exit 1
    fi
fi

if ! command -v keytool &> /dev/null;then
    echo "Keytool could not be found. Please install it and try again."
    exit 1
else
    echo "Keytool found in Java, Java information: $(java -version 2>&1 | head -n 1)"
fi

# 解析命令行参数
SCRIPT_NAME=$(basename "$0") # 获取脚本文件名
while getopts "hc:o:u:r:s:p:d:t:k:i:" opt; do
  case ${opt} in
     h)
      echo "Usage:"
      echo "    $SCRIPT_NAME -h/help            显示帮助信息."
      echo "    $SCRIPT_NAME -c COUNTRY_NAME    设置证书国家名称 (default is '$COUNTRY_NAME')."
      echo "    $SCRIPT_NAME -o ORG_NAME        设置证书组织名称 (default is '$ORG_NAME')."
      echo "    $SCRIPT_NAME -u OU_NAME         设置证书组织单元名称 (default is '$OU_NAME')."
      echo "    $SCRIPT_NAME -r CN_ROOT         设置根证书通用名称 (default is '$CN_ROOT')."
      echo "    $SCRIPT_NAME -s CN_SUB          设置子证书通用名称 (default is '$CN_SUB')."
      echo "    $SCRIPT_NAME -p PASSWD          设置keystore与truststore密码 (default is '$PASSWD')."
      echo "    $SCRIPT_NAME -d DURATION_DAYS   设置证书有效时长 (default is '$DURATION_DAYS' days)."
      echo "    $SCRIPT_NAME -t ROOT_CRT        设置客户证书文件 (default is '$ROOT_CRT')."
      echo "    $SCRIPT_NAME -k ROOT_KEY        设置客户证书秘钥 (default is '$ROOT_KEY')."
      echo "    $SCRIPT_NAME -i CACERTS         为Truststore文件添加信任库"
      exit 0
      ;;
    help)
      echo "Usage:"
      echo "    $SCRIPT_NAME -h/help            显示帮助信息."
      echo "    $SCRIPT_NAME -c COUNTRY_NAME    设置证书国家名称 (default is '$COUNTRY_NAME')."
      echo "    $SCRIPT_NAME -o ORG_NAME        设置证书组织名称 (default is '$ORG_NAME')."
      echo "    $SCRIPT_NAME -u OU_NAME         设置证书组织单元名称 (default is '$OU_NAME')."
      echo "    $SCRIPT_NAME -r CN_ROOT         设置根证书通用名称 (default is '$CN_ROOT')."
      echo "    $SCRIPT_NAME -s CN_SUB          设置子证书通用名称 (default is '$CN_SUB')."
      echo "    $SCRIPT_NAME -p PASSWD          设置keystore与truststore密码 (default is '$PASSWD')."
      echo "    $SCRIPT_NAME -d DURATION_DAYS   设置证书有效时长 (default is '$DURATION_DAYS' days)."
      echo "    $SCRIPT_NAME -t ROOT_CRT        设置客户证书文件 (default is '$ROOT_CRT')."
      echo "    $SCRIPT_NAME -k ROOT_KEY        设置客户证书秘钥 (default is '$ROOT_KEY')."
      echo "    $SCRIPT_NAME -i CACERTS         为Truststore文件添加信任库"
      exit 0
      ;;
    c)
      COUNTRY_NAME=$OPTARG
      ;;
    o)
      ORG_NAME=$OPTARG
      ;;
    u)
      OU_NAME=$OPTARG
      ;;
    r)
      CN_ROOT=$OPTARG
      ;;
    s)
      CN_SUB=$OPTARG
      ;;
    p)
      PASSWD=$OPTARG
      ;;
    d)
      DURATION_DAYS=$OPTARG
      ;;
    t)
      ROOT_CRT=$OPTARG
      ;;
    k)
      ROOT_KEY=$OPTARG
      ;;
    i)
      ONLY_TRUSTSTORE=true
      ROOT_CRT=$OPTARG
      ;;
    \?)
      echo "Invalid option: -$OPTARG" 1>&2
      exit 1
      ;;
    :)
      echo "Option -$OPTARG requires an argument." 1>&2
      exit 1
      ;;
  esac
done
shift $((OPTIND -1))


# 定义别名alias_name
ALIAS_NAME=$(generate_random_name)
# 定义keystore随机密码,过滤掉输出中的非字母数字字符，只保留字母和数字。
KEYSTORE_PASSWD=$(openssl rand -base64 12 | tr -dc '[:alnum:]')
#KEYSTORE_PASSWD=$PASSWD
# 获取当前时间
current_time=$(date +"%Y-%m-%d %H:%M:%S")
# 打印结果到 results.txt 文件
cat >> results.log <<EOF
+------------------------------------------------------------------+
| Update # $current_time                                     |
+------------------------------------------------------------------+
EOF


# 1. 生成根证书文件与秘钥：当用户没有指定根证书或者根秘钥时，以及用户没有输入用 -i 选项（即非单独更新cacerts）时执行
if [ ! -e $ROOT_CRT ] || [ ! -e $ROOT_KEY ] && [ -z "$ONLY_TRUSTSTORE" ]; then
    generate_certificate "openssl req -x509 -newkey rsa:4096 -sha256 -days $DURATION_DAYS -keyout $ROOT_KEY -out $ROOT_CRT -config root.cnf -nodes" \
    "Failed to generate root certificate and key." \
    "Successfully generate root cert ($ROOT_CRT) and key file ($ROOT_KEY)"
    cat >> results.log <<EOF
| Root certificate:  $ROOT_CRT
| Root key:         $ROOT_KEY
EOF
fi

# 2.生成子证书文件与秘钥：用户没有输入用 -i 选项（即非单独更新cacerts）时执行
if [ -z "$ONLY_TRUSTSTORE" ]; then
# 生成子证书的私钥和证书签名请求
  generate_certificate "openssl req -new -newkey rsa:3072 -keyout $SUB_KEY -out sub.csr -config sub.cnf -nodes" \
   "Failed to generate sub key and certificate signing request." \
   "Successfully generate sub key ($SUB_KEY) and certificate signing request (sub.csr)"
# 使用根证书签名CSR，生成的子证书就会由根证书签名，形成证书链。
  generate_certificate "openssl x509 -req -in sub.csr -CA $ROOT_CRT -CAkey $ROOT_KEY -CAcreateserial -out $SUB_CRT -days $DURATION_DAYS -extensions v3_sub -extfile sub.cnf" \
   "Failed to generate sub certificate." \
   "Successfully generate sub cert ($SUB_CRT) with root cert ($ROOT_CRT)"
  
  cat >> results.log <<EOF
| Root certificate:  $SUB_CRT
| Root key:         $SUB_KEY 
EOF
fi

# 3. 生成 Keystore 文件：用户没有输入用 -i 选项（即非单独更新cacerts）时执行
if [ -z "$ONLY_TRUSTSTORE" ]; then
  generate_keystore $SUB_CRT $SUB_KEY $JAVA_KEYSTORE $ALIAS_NAME $KEYSTORE_PASSWD
  cat >> results.log <<EOF
| Keystore file:     $JAVA_KEYSTORE
| Keystore password: $KEYSTORE_PASSWD
| Keystore alias:    $ALIAS_NAME
EOF
fi

# 4. 生成 Truststore 文件，任何时候都会生成Truststore文件，即更新Cacerts信任库
generate_truststore $ALIAS_NAME $ROOT_CRT $JAVA_TRUSTSTORE $PASSWD
cat >> results.log <<EOF
| Truststore file:    $JAVA_TRUSTSTORE
| Truststore password:  $PASSWD
| Truststore alias:    $ALIAS_NAME
EOF

# 6. 清理临时文件
# 清理临时文件
echo "---------------------------------------------------"
echo "Cleaning up temporary files ..."
clean_files *.cnf  *.csr *.srl
echo "---------------------------------------------------"

