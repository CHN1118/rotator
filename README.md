
## macOS (通过 Homebrew)
``` javascript
brew install tor
```

## 创建文件和目录
```javascript
nano /opt/homebrew/etc/tor/torrc

mkdir /opt/homebrew/var/lib/tor/
```

## 配置torrc文件
```text
# 使用 ClashX 的 SOCKS5 代理作为 Tor 的出口代理
Socks5Proxy 127.0.0.1:7890
# 端口根据 ClashX 的代理端口进行修改
# 禁用代理的证书检查
TestSocks 0

# 隐藏服务配置（确保目录权限正确）
HiddenServiceDir /opt/homebrew/var/lib/tor/hs1/
HiddenServicePort 80 127.0.0.1:8080

HiddenServiceDir /opt/homebrew/var/lib/tor/hs2/
HiddenServicePort 80 127.0.0.1:8080

HiddenServiceDir /opt/homebrew/var/lib/tor/hs3/
HiddenServicePort 80 127.0.0.1:8080

# 避免因网络延迟导致的卡顿
ConnectionPadding 0
# ReduceConnectionPadding 1

# 禁用某些可能干扰代理的功能
UseMicrodescriptors 0
AvoidDiskWrites 1

```

## 运行tor
```javascript
tor -f /opt/homebrew/etc/tor/torrc
```