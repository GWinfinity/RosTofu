# RosTofu ROS 发布流程指南

## 📋 发布前检查清单

### ✅ 已完成
- [x] package.xml 已配置
- [x] setup.py 已配置
- [x] LICENSE 文件 (Apache-2.0)
- [x] 源代码仓库: https://github.com/GWinfinity/RosTofu

### 📝 需要手动确认
- [ ] 版本号是否正确 (当前: 0.2.0)
- [ ] maintainer_email 是否有效 (已更新: dev@gwinfinity.tech)
- [ ] 所有依赖是否已声明

---

## 🚀 发布步骤

### 步骤 1: 安装 bloom

```bash
# Ubuntu/Debian
sudo apt-get install python3-bloom

# 或使用 pip
pip install bloom
```

### 步骤 2: 初始化 bloom

```bash
# 进入包目录
cd ~/RosPaw/rostofu_bringup

# 初始化 bloom (如果是第一次发布)
bloom-release --rosdistro humble --track humble rostofu_bringup --edit
```

### 步骤 3: 创建 Release Repository

你需要在 GitHub 上创建一个 release 仓库（如果还没有）：

1. 访问 https://github.com/new
2. 仓库名称: `rostofu_bringup-release`
3. 选择 Public
4. 创建空仓库（不要初始化 README）

### 步骤 4: 配置 bloom

创建/编辑 `rostofu_bringup` 的 tracks.yaml：

```bash
# 配置 track
bloom-release --rosdistro humble --track humble rostofu_bringup --edit
```

配置内容参考：
```yaml
name: rostofu_bringup
type: git
url: https://github.com/GWinfinity/RosTofu.git
version: :{auto}
release_repo_url: https://github.com/GWinfinity/rostofu_bringup-release.git
```

### 步骤 5: 执行发布

```bash
# 执行 bloom 发布
bloom-release --rosdistro humble --track humble rostofu_bringup --new-track
```

这个命令会：
1. 克隆源代码
2. 生成 Debian 包配置
3. 创建 release 仓库的 PR
4. 生成 rosdistro 的 PR

### 步骤 6: 提交 rosdistro PR

bloom 会自动生成 PR 到 ros/rosdistro，如果没有自动生成，手动提交：

1. Fork https://github.com/ros/rosdistro
2. 编辑 `humble/distribution.yaml`，添加：

```yaml
rostofu_bringup:
  source:
    type: git
    url: https://github.com/GWinfinity/RosTofu.git
    version: main
  release:
    tags:
      release: release/humble/{package}/{version}
    url: https://github.com/GWinfinity/rostofu_bringup-release.git
    version: 0.2.0-1
  status: developed
```

3. 提交 PR 到 ros/rosdistro

---

## 📊 发布后验证

### 检查构建状态
- 访问: http://repo.ros2.org/status_page/ros_humble_default.html
- 搜索: `rostofu_bringup`

### 检查索引
- 访问: https://index.ros.org/p/rostofu_bringup/

### 安装测试
```bash
sudo apt update
sudo apt install ros-humble-rostofu-bringup
```

---

## 🔧 常见问题

### Q1: bloom 报错 "No track found"
```bash
# 创建新 track
bloom-release --rosdistro humble --track humble rostofu_bringup --new-track
```

### Q2: 依赖问题
确保 `package.xml` 中所有 `<depend>` 都有对应的 rosdep key：
```bash
rosdep check rostofu_bringup
```

### Q3: 版本冲突
如果更新版本，记得同步修改：
- package.xml: `<version>x.x.x</version>`
- setup.py: `version='x.x.x'`

---

## 📞 需要帮助

- ROS 发布文档: https://docs.ros.org/en/humble/How-To-Guides/Releasing/Releasing-a-Package.html
- Bloom 文档: https://bloom.readthedocs.io/
- rosdistro PR 审核: https://github.com/ros/rosdistro/pulls
