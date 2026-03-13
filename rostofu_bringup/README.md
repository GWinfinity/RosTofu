# rostofu_bringup

ROS2 包，用于封装和启动 tofu 应用程序。
支持 Windows 和 Linux/Ubuntu 双平台。

## 目录结构

```
rostofu_bringup/
├── package.xml          # ROS2 包描述
├── setup.py             # Python 包配置
├── README.md            # 本文件
├── launch/
│   └── tofu_launch.py  # Launch 文件
├── resource/
│   └── rostofu_bringup   # 资源标记文件
└── rostofu_bringup/
    ├── __init__.py
    └── tofu_node.py    # 主要的 ROS2 节点
```

## 使用步骤

### 1. 激活 ROS2 环境

**Windows (PowerShell):**
```powershell
# 根据你的 ROS2 安装路径
& C:\opt\ros\humble\local_setup.ps1
# 或
& C:\opt\ros\jazzy\local_setup.ps1
```

**Linux/Ubuntu (Bash):**
```bash
# 根据你的 ROS2 版本
source /opt/ros/humble/setup.bash
# 或
source /opt/ros/jazzy/setup.bash
```

### 2. 构建包

**Windows:**
```powershell
cd D:\githbi\RosTofu
colcon build --packages-select rostofu_bringup
```

**Linux/Ubuntu:**
```bash
cd ~/RosTofu  # 或你的项目路径
colcon build --packages-select rostofu_bringup
```

### 3. 激活工作空间

**Windows:**
```powershell
.\install\local_setup.ps1
```

**Linux/Ubuntu:**
```bash
source install/setup.bash
```

### 4. 启动 tofu 服务

**方法1：使用 ros2 run**

**Windows:**
```powershell
ros2 run rostofu_bringup tofu_node
```

**Linux/Ubuntu:**
```bash
ros2 run rostofu_bringup tofu_node
```

**方法2：使用 launch 文件**

**Windows:**
```powershell
ros2 launch rostofu_bringup tofu_launch.py
```

**Linux/Ubuntu:**
```bash
ros2 launch rostofu_bringup tofu_launch.py
```

**指定参数启动：**

**Windows:**
```powershell
ros2 launch rostofu_bringup tofu_launch.py tofu_path:="D:\\githbi\\RosTofu\\.venv\\Scripts\\tofu.exe"
```

**Linux/Ubuntu:**
```bash
ros2 launch rostofu_bringup tofu_launch.py tofu_path:="/home/username/RosTofu/.venv/bin/tofu"
```

## 服务接口

启动节点后，可以使用以下 ROS2 服务控制 tofu：

```bash
# 启动 tofu
ros2 service call /start_tofu std_srvs/srv/Trigger

# 停止 tofu
ros2 service call /stop_tofu std_srvs/srv/Trigger

# 重启 tofu
ros2 service call /restart_tofu std_srvs/srv/Trigger
```

## 话题

- `/tofu_status` (std_msgs/String): 发布 tofu 的运行状态

```bash
# 查看状态
ros2 topic echo /tofu_status
```

## 参数

| 参数名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `tofu_path` | string | `""` | tofu 可执行文件的路径，留空则自动检测 |
| `working_directory` | string | `""` | tofu 工作目录 |
| `auto_start` | bool | `true` | 节点启动时自动启动 tofu |

## 可执行文件路径

包会自动检测以下位置的 tofu 可执行文件：

**Windows:**
- `.venv\Scripts\tofu.exe`
- `venv\Scripts\tofu.exe`
- PATH 环境变量中的 `tofu`

**Linux/Ubuntu:**
- `.venv/bin/tofu`
- `venv/bin/tofu`
- `~/RosTofu/.venv/bin/tofu`
- `/opt/rostofu/.venv/bin/tofu`
- PATH 环境变量中的 `tofu`

如果无法自动检测到，请通过参数 `tofu_path` 显式指定。

## 注意事项

1. **ROS2 环境**：确保 ROS2 已正确安装和配置
2. **tofu 可执行文件**：必须在虚拟环境中可用或存在于 PATH 中
3. **权限**：在 Linux 上，确保 tofu 有执行权限 (`chmod +x tofu`)
4. **进程管理**：
   - Windows：使用进程组管理
   - Linux：使用进程组和会话管理，支持优雅关闭
