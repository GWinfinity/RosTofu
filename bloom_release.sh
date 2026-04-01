#!/bin/bash
# RosTofu Bloom 发布脚本

set -e

# 配置
PACKAGE_NAME="rostofu_bringup"
ROS_DISTRO="humble"
SOURCE_URL="https://github.com/GWinfinity/RosTofu.git"
RELEASE_URL="https://github.com/GWinfinity/rostofu_bringup-release.git"

echo "========================================"
echo "  RosTofu Bloom 发布脚本"
echo "========================================"
echo ""

# 检查 bloom 是否安装
if ! command -v bloom-release &> /dev/null; then
    echo "❌ bloom 未安装，请先安装:"
    echo "   sudo apt-get install python3-bloom"
    exit 1
fi

echo "✓ bloom 已安装"

# 检查 git 配置
if [ -z "$(git config --global user.name)" ] || [ -z "$(git config --global user.email)" ]; then
    echo "❌ git 用户配置不完整，请先配置:"
    echo "   git config --global user.name 'Your Name'"
    echo "   git config --global user.email 'your@email.com'"
    exit 1
fi

echo "✓ git 配置正确"

# 检查当前目录
cd rostofu_bringup

# 检查 package.xml
if [ ! -f "package.xml" ]; then
    echo "❌ package.xml 不存在"
    exit 1
fi

echo "✓ package.xml 存在"

# 获取版本号
VERSION=$(grep -oP '(?<=<version>)[^<]+' package.xml)
echo "📦 包版本: $VERSION"

# 检查 setup.py 版本是否一致
if [ -f "setup.py" ]; then
    SETUP_VERSION=$(grep -oP "(?<=version=')[^']+" setup.py)
    if [ "$VERSION" != "$SETUP_VERSION" ]; then
        echo "⚠️ 警告: package.xml 版本 ($VERSION) 与 setup.py 版本 ($SETUP_VERSION) 不一致"
        echo "   请统一版本号后再发布"
        exit 1
    fi
    echo "✓ 版本号一致"
fi

cd ..

echo ""
echo "========================================"
echo "  开始 Bloom 发布流程"
echo "========================================"
echo ""

# 检查是否有现有 track
echo "📋 检查 bloom track..."
if bloom-release "$ROS_DISTRO" --list-tracks 2>/dev/null | grep -q "^${PACKAGE_NAME}$"; then
    echo "✓ 已存在 track，执行更新发布"
    bloom-release --rosdistro "$ROS_DISTRO" --track "$ROS_DISTRO" "$PACKAGE_NAME"
else
    echo "🆕 未找到 track，创建新 track"
    echo ""
    echo "请确保已创建 release 仓库:"
    echo "  $RELEASE_URL"
    echo ""
    read -p "确认已创建 release 仓库并按回车继续..."
    
    bloom-release --rosdistro "$ROS_DISTRO" --track "$ROS_DISTRO" "$PACKAGE_NAME" --new-track
fi

echo ""
echo "========================================"
echo "  发布完成！"
echo "========================================"
echo ""
echo "后续步骤:"
echo "1. 检查生成的 PR: https://github.com/ros/rosdistro/pulls"
echo "2. 等待 ROS Boss 审核"
echo "3. 检查构建状态: http://repo.ros2.org/status_page/ros_humble_default.html"
echo ""
