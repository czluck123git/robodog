"""
GUI原厂动作功能快速验证脚本
检查GUI是否能正确加载原厂动作模块
"""

import sys
import os

# 添加路径
sys.path.append('.')
sys.path.append('..')

def test_gui_factory_actions_integration():
    """测试GUI与原厂动作模块的集成"""
    print("🏭 GUI原厂动作功能集成测试")
    print("=" * 50)
    
    try:
        # 测试导入
        print("1. 测试模块导入...")
        from robodog.factory_actions import FactoryActions, FactoryAction
        print("   ✅ factory_actions模块导入成功")
        
        from GUI.unified_control import RobodogUnifiedGUI
        print("   ✅ GUI模块导入成功")
        
        # 测试GUI初始化（不启动mainloop）
        print("\n2. 测试GUI初始化...")
        app = RobodogUnifiedGUI()
        print("   ✅ GUI初始化成功")
        
        # 检查原厂动作区域是否正确初始化
        print("\n3. 检查原厂动作功能集成...")
        widgets_to_check = ['factory_combo', 'factory_exec_btn', 'factory_stop_btn',
                           'factory_status_label', 'factory_action_var']
        for widget in widgets_to_check:
            if hasattr(app, widget):
                print(f"   ✅ {widget} 已创建")
            else:
                print(f"   ❌ {widget} 缺失")
                return False
        
        # 检查GUI是否有原厂动作相关方法
        print("\n4. 检查GUI原厂动作方法...")
        methods_to_check = ['setup_factory_actions_area', 'refresh_factory_actions',
                           'execute_factory_action', 'stop_factory_action',
                           '_run_factory_action', 'get_factory_display_name']
        for method in methods_to_check:
            if hasattr(app, method):
                print(f"   ✅ {method} 方法存在")
            else:
                print(f"   ❌ {method} 方法缺失")
                return False
        
        # 检查快捷动作配置
        print("\n5. 检查快捷动作配置...")
        if hasattr(app, 'factory_quick_actions') and len(app.factory_quick_actions) > 0:
            print(f"   ✅ 已配置 {len(app.factory_quick_actions)} 个快捷动作:")
            for name, aid in app.factory_quick_actions:
                print(f"      • {name} (ID:{aid})")
        else:
            print("   ❌ 快捷动作未配置")
            return False
        
        print("\n🎉 GUI原厂动作功能集成测试通过!")
        print("\n📋 GUI启动指南:")
        print("1. 确保机器狗已连接")
        print("2. 进入GUI目录: cd GUI")
        print("3. 运行GUI: python unified_control.py")
        print("4. 连接机器狗后，在'🏭 原厂动作'区域测试动作")
        
        return True
        
    except ImportError as e:
        print(f"   ❌ 导入错误: {e}")
        return False
    except Exception as e:
        print(f"   ❌ 其他错误: {e}")
        return False

def test_robot_connection(host='192.168.101.215'):
    """连接真实机器人测试原厂动作模块（可选）"""
    print("\n" + "=" * 60)
    print(f"🤖 真机连接测试: {host}")
    print("=" * 60)
    
    try:
        import roslibpy
        from robodog.factory_actions import FactoryActions
        
        print("\n1. 连接机器人...")
        client = roslibpy.Ros(host=host, port=9090)
        client.run()
        if not client.is_connected:
            print("   ❌ 连接失败")
            return False
        print("   ✅ 连接成功")
        
        fa = FactoryActions(client)
        
        print("\n2. 获取原厂动作列表...")
        actions = fa.get_available_actions(timeout=5.0)
        print(f"   ✅ 获取到 {len(actions)} 个动作:")
        for a in actions:
            print(f"      • ID {a.action_id}: {a.name}")
        
        client.terminate()
        print("\n🎉 真机连接测试通过!")
        return True
        
    except Exception as e:
        print(f"   ❌ 真机测试失败: {e}")
        return False

def show_usage_guide():
    """显示使用指南"""
    print("\n" + "=" * 60)
    print("🎯 机器狗原厂动作使用指南")
    print("=" * 60)
    
    print("\n📍 步骤1: 启动GUI")
    print("   cd GUI")
    print("   python unified_control.py")
    
    print("\n📍 步骤2: 连接机器狗")
    print("   - 输入机器狗IP地址 (默认: 192.168.101.215)")
    print("   - 点击'连接'按钮")
    print("   - 等待连接成功，动作列表会自动加载")
    
    print("\n📍 步骤3: 执行原厂动作")
    print("   方式一 - 下拉框选择:")
    print("   - 在'🏭 原厂动作'区域的下拉框中选择动作")
    print("   - 点击'执行动作'按钮")
    print("   方式二 - 快捷按钮:")
    print("   - 点击常用动作按钮 (唤醒/坐下/趴下/恢复站立/摇摆/握手/动态舞蹈)")
    
    print("\n📍 步骤4: 停止动作")
    print("   - 点击'停止动作'按钮可随时取消")
    print("   - 出现异常时使用'紧急停止'")
    
    print("\n⚠️ 安全注意事项:")
    print("   - 执行动作前确保机器狗周围有足够空间")
    print("   - 空翻类动作(后空翻/前空翻等)请在开阔场地使用")
    print("   - 动作执行过程中请勿触碰机器狗")

if __name__ == "__main__":
    success = test_gui_factory_actions_integration()
    
    # 可选: 真机测试 (传入 --robot 参数)
    if '--robot' in sys.argv:
        robot_ok = test_robot_connection()
        success = success and robot_ok
    
    if success:
        show_usage_guide()
        print(f"\n✨ 原厂动作系统准备就绪!")
        if '--robot' not in sys.argv:
            print("💡 提示: 使用 --robot 参数可连接真实机器人测试")
    else:
        print(f"\n❌ 集成测试失败，请检查配置")
