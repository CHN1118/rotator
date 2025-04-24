
## macOS (通过 Homebrew)
``` javascript
brew install tor
```

## 创建文件和目录
```javascript
nano /opt/homebrew/etc/tor/torrc

mkdir /opt/homebrew/var/lib/tor/

mkdir /opt/homebrew/var/lib/tor/fixed_onion

mkdir /opt/homebrew/var/lib/tor/rotating_onion
```
#### fixed_onion用于存放固定 onion
#### rotating_onion用于存放动态 onion

## 配置torrc文件
```text
ControlPort 9051
HashedControlPassword 16:6A1A071D9A305F1760680E27E78B84D1965C53163BF3585B9B7C802DCA

# 使用 ClashX 的 SOCKS5 代理作为 Tor 的出口代理
Socks5Proxy 127.0.0.1:62938
# 禁用代理的证书检查
TestSocks 0

# 避免因网络延迟导致的卡顿
ConnectionPadding 0
# ReduceConnectionPadding 1

# 禁用某些可能干扰代理的功能
UseMicrodescriptors 0
AvoidDiskWrites 1

# 隐藏服务配置（确保目录权限正确）
```
#### Socks5Proxy 端口根据本地代理自行配置
#### HashedControlPassword 对应的密码为 rotatorpsw

## 运行tor
```javascript
tor -f /opt/homebrew/etc/tor/torrc
```

